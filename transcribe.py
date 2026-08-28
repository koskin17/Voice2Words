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
    chunk_ms: int = 60000,
    language: str | None = None,
    output_txt: str | Path = "transcribe.txt",
    ) -> Path:
    """
    Convert audio file, split it into chunks, transcribe each chunk with Wosper and save the result to TXT.
    """
    
    mp3_path = Path(mp3_path)
    output_txt = Path(output_txt)
    
    # 1. Validate input parametrs
    if not mp3_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {mp3_path}"
        )
        
    if not mp3_path.is_file():
        raise ValueError(
            f"Input path is not a file: {mp3_path}"
        )
        
    if model_size not in VALID_MODELS:
        raise ValueError(
            f"Unknown Whisper model: {model_size}"
            f"Available models: {', '.join(sorted(VALID_MODELS))}"
        )
        
    if chunk_ms <= 0:
        raise ValueError(
            "chunk_ms must be greater than 0"
        )
    
    output_txt.parent.mkdir(parents=True, exist_ok=True,)
    
    # 2. Create temporary working directory
    temp_dir = Path(tempfile.mkdtemp(prefix="whisper_transcribe_"))
    wav_path = temp_dir / "audio.wav"
    chunks_dir = temp_dir / "chunks"
    
    logger.info("Temporary directory: %s", temp_dir)
    
    #3. Convert input audio to wav
    logger.info("Converting input audio: %s", mp3_path)
    
    mp3_to_wav(mp3_path, wav_path,)
    
    #4. Split WAV into chunks
    logger.info("Splitting audio into %d ms chunks", chunk_ms,)
    
    chunks = split_wav(wav_path, chunk_length_ms=chunk_ms, out_dir=chunks_dir,)
    
    if not chunks:
        raise RuntimeError("no audio chunks were created")
    
    #5. Load Whisper model
    logger.info("Loading Whisper model: %s", model_size)
    
    try:
        model = whisper.load_model(model_size)
    except Exception as e:
        raise RuntimeError(
            f"Failed to load Whisper model '{model_size}'."
            ) from e
        
    #6. Transcribe chunks
    logger.info("Starting transcription of % chunks.")
    
    with output_txt.open("w", encoding="utf-8") as output_file:
        for index, chunk in enumerate(chunks, start = 1):
            logger.info("Transcribing chunk %d/%d: %s", index, len(chunks), chunk.name,)
            
            try:
                if language:
                    result = model.transcribe(str(chunk), language = language,)
                else:
                    result = model.transcribe(str(chunk))
            except Exception as e:
                logger.error(
                    "Failed to transcribe chunk %d/%d: %s", index, len(chunks), e,
                )
    
    # 1. Convert and partition the audio file
    wav_path = "temp_output.wav"
    mp3_to_wav(mp3_path, wav_path)
    chunks = split_wav(wav_path, chunk_length_ms = chunk_ms, out_dir = "chunks")
    
    # 2. Load the Whisper model
    model = whisper.load_model(model_size)
    
    #3. Transcribe each chunk and save the results
    with open(output_txt, "w", encoding = "utf_8") as f:
        for chunk in chunks:
            print("Transcribing: ", chunk)
            result = model.transcribe(chunk, language = language) if language else model.transcribe(chunk)
            text = result.get("text", "").strip()
            f.write(text + "\n")
            
    print("Transcription save to: ", output_txt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help = "input mp3 file")
    parser.add_argument("--model", default = "medium", help = "whisper model size (tiny, base, small, medium, large)")
    parser.add_argument("--chunk_ms", type = int, default = 60000, help = "chunk lenght in milliseconds")
    parser.add_argument("--language", default = None, help = "language code (e.g., ru, en) or leave empty for auto-detect")
    parser.add_argument("--out", default = "transcript.txt", help = "output test file")
    args = parser.parse_args()
    
    transcribe_file(args.input, model_size = args.model, chunk_ms = args.chunk_ms, language = args.language, output_txt = args.out)