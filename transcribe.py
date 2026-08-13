import whisper
import os
import argparse
from convert import mp3_to_wav, split_wav


def transcribe_file(mp3_path, model_size = "small", chunk_ms = 60000, language = None, output_txt = "transcribe.txt"):
    # 1. Convert and partition the audio file
    wav_path = "temp_output.wav"
    mp3_to_wav(mp3_path, wav_path)
    chunks = split_wav(wav_path, chunk_lenght_ms = chunk_ms, out_dir = "chunks")
    
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