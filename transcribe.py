from pathlib import Path
import whisper
import argparse
import logging
import shutil
import tempfile

from convert import mp3_to_wav, split_wav


logger = logging.getLogger(__name__)

DEFAULT_MODEL = "medium"
DEFAULT_CHUNK_MS = 60000

VALID_MODELS = {
    "tiny",
    "base",
    "small",
    "medium",
    "large",
}

def transcribe_file(
    mp3_path: str | Path,
    model_size: str = DEFAULT_MODEL,
    chunk_ms: int = DEFAULT_CHUNK_MS,
    language: str | None = None,
    output_txt: str | Path = "transcribe.txt",
    progress_callback=None,
    ) -> Path:
    """
    Convert audio file, split it into chunks, transcribe each chunk with Whisper and save the result to TXT.
    """

    mp3_path = Path(mp3_path)
    output_txt = Path(output_txt)

    # 1. Validate input parameters
    if not mp3_path.exists():
        raise FileNotFoundError(f"Input file not found: {mp3_path}")

    if not mp3_path.is_file():
        raise ValueError(f"Input path is not a file: {mp3_path}")

    if model_size not in VALID_MODELS:
        raise ValueError(
            f"Unknown Whisper model: {model_size}. "
            f"Available models: {', '.join(sorted(VALID_MODELS))}"
        )

    try:
        chunk_ms = int(chunk_ms)
    except (TypeError, ValueError) as e:
        raise ValueError("chunk_ms must be an integer") from e

    if chunk_ms <= 0:
        raise ValueError("chunk_ms must be greater than 0")

    if language is not None:
        language = language.strip() or None

    output_txt.parent.mkdir(parents=True, exist_ok=True)

    # 2. Create temporary working directory
    temp_dir = Path(tempfile.mkdtemp(prefix="whisper_transcribe_"))
    wav_path = temp_dir / "audio.wav"
    chunks_dir = temp_dir / "chunks"

    logger.info("Temporary directory: %s", temp_dir)

    try:
        # 3. Convert input audio to wav
        logger.info("Converting input audio: %s", mp3_path)
        mp3_to_wav(mp3_path, wav_path)

        # 4. Split WAV into chunks
        logger.info("Splitting audio into %d ms chunks", chunk_ms)
        chunks = split_wav(wav_path, chunk_length_ms=chunk_ms, out_dir=chunks_dir)

        if not chunks:
            raise RuntimeError("No audio chunks were created")

        # 5. Load Whisper model
        logger.info("Loading Whisper model: %s", model_size)
        try:
            model = whisper.load_model(model_size)
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model '{model_size}'.") from e

        # 6. Transcribe chunks
        logger.info("Starting transcription of %d chunks.", len(chunks))

        with output_txt.open("w", encoding="utf-8") as output_file:
            for index, chunk in enumerate(chunks, start=1):
                chunk_message = f"Transcribing chunk {index} / {len(chunks)}"
                logger.info(chunk_message)
                
                if progress_callback is not None:
                    progress_callback(chunk_message)

                try:
                    if language:
                        result = model.transcribe(str(chunk), language=language, fp16=False)
                    else:
                        result = model.transcribe(str(chunk), fp16=False)
                except Exception as e:
                    logger.error("Failed to transcribe chunk %d/%d: %s", index, len(chunks), e)
                    raise RuntimeError(
                        f"Transcription failed for chunk {index} / {len(chunks)}"
                    ) from e

                text = result.get("text", "").strip()

                if text:
                    output_file.write(text + "\n")

                output_file.flush()

                progress_percent = (index / len(chunks) * 100)
                logger.info("Progress: %.1f%%", progress_percent)

            logger.info("Transcription saved to: %s", output_txt)

        return output_txt

    finally:
        # 7. Cleanup temporary files
        if temp_dir.exists():
            logger.info("Cleaning temporary files...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            
def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe audio file useing Whisper")
    parser.add_argument("input", help = "Input audio file",)
    parser.add_argument("--model", default = DEFAULT_MODEL, choices = sorted(VALID_MODELS), help = "Whisper model size",)
    parser.add_argument("--chunk_ms", type = int, default=DEFAULT_CHUNK_MS, help = "Chunk length in milliseconds",)
    parser.add_argument("--language", default = None, help = ("Language code: eng or ru." "Leave empy for automatic language detection.",))
    parser.add_argument("--out", default = "transcript.txt", help = "Output text file.")
    
    args = parser.parse_args()
    
    logging.basicConfig(level = logging.INFO, format = "%(filename)s: %(message)s",)
    
    try:
        output = transcribe_file(
            args.input,
            model_size = args.model,
            chunk_ms = args.chunk_ms,
            language = args.language,
            output_txt = args.out,
            )
        
        print(f"\nTranscription completed succassfully: {output}")
        
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        logger.error("%s", e)
        raise SystemExit(1)
    
if __name__ == "__main__":
    main()
