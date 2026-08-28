from pathlib import Path
import argparse
import logging
from pydub import AudioSegment


logger = logging.getLogger(__name__)


def mp3_to_wav(
    input_path: str | Path,
    output_path: str | Path,
    target_sr: int = 16000,
    ) -> Path:
    """
    Convert audio file to mono WAV with the specified sample rate.
    """
    
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")
    
    if target_sr <= 0:
        raise ValueError("target_sr must be greater than 0")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info("Loading audio: %s", input_path)
    
    try:
        audio = AudioSegment.from_file(input_path)
    except Exception as e:
        raise RuntimeError(
            f"Failed to read audio file '{input_path}'."
            f"Make sure the file is valid and FFmpeg is installed."
        ) from e
        
    audio = audio.set_frame_rate(target_sr).set_channels(1)
    
    logger.info("Converting audio to WAV: %s Hz mono", target_sr,)
    
    try:
        audio.export(output_path, format = "wav")
    except Exception as e:
        raise RuntimeError(
            f"Failed to export WAV file: {output_path}"
        ) from e
        
    logger.info("WAV saved: %s", output_path)
    
    return output_path

def split_wav(
    wav_path: str | Path,
    chunk_length_ms: int = 60000,
    out_dir: str | Path = "chunks",
    ) -> list[Path]:
    """
    Split WAV file into chunks of the specified length.
    """
    
    wav_path = Path(wav_path)
    out_dir = Path(out_dir)
    
    if not wav_path.exist():
        raise FileNotFoundError(f"WAV file not found: {wav_path}")
    
    if not wav_path.is_file():
        raise FileNotFoundError(f"WAV path is not a file: {wav_path}")
    
    if chunk_length_ms <= 0:
        raise ValueError("chunk_length_ms must be greater than 0")
    
    out_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Loading WAV file: %s", wav_path)
    
    try:
        audio = AudioSegment.from_wav(wav_path)
    except Exception as e:
        raise RuntimeError(
            f"Failed to read WAV file: {wav_path}"
        ) from e
        
    duration_ms = len(audio)
    
    if duration_ms == 0:
        raise ValueError(f"WAV file is empty: {wav_path}")
    
    chunks: list[Path] = []
    
    chunk_number = 1
    
    for start_ms in range(0, duration_ms, chunk_length_ms):
        end_ms = min(start_ms + chunk_length_ms, duration_ms)
        
        chunk = audio[start_ms:end_ms]
        
        chunk_name = out_dir / f"chunk_{chunk_number:04d}.wav"
        
        try:
            chunk.export(chunk_name, format = "wav")
        except Exception as e:
            raise RuntimeError(
                f"Failed to export chunk: {chunk_name}"
            ) from e
            
        chunk.append(chunk_name)
        
        logger.debug(
            "Created chunk %d: %d-%d ms",
            chunk_number,
            start_ms,
            end_ms,
        )
    
        chunk_number += 1
        
    logger.info("Created %d audio chunks", len(chunk))
    
    return chunks

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert audio file to WAV and split it into chunks."
    )
    
    parser.add_argument(
        "input",
        help = "Input audio file",
    )
    
    parser.add_argument(
        "--wav",
        default = "output.wav",
        help = "Output WAV file",
    )
    
    parser.add_argument(
        "--chunk_ms",
        type = int,
        default=60000,
        help = "Chunk length in milliseconds",
    )
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level = logging.INFO,
        format = "%(levelname)s: %(message)s",
    )
    
    try:
        wav_path = mp3_to_wav(args.input, args.wav,)
        print(f"WAV saved: {wav_path}")
        chunks = split_wav(wav_path, chunk_length_ms = args.chunk_ms,)
        print(f"Created {len(chunks)} chunks.")
        
        for chunk in chunks:
            print(chunk)
            
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        logger.error("%s", e)
        raise SystemExit(1)
    
if __name__ == "__main__":
    main()
    