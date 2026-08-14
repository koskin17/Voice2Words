import whisper
from convert import mp3_to_wav, split_wav


def transcribe_file(mp3_path, model_size = "small", chunk_ms = 60000, language = None, output_txt = "transcribe.txt"):
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
            
    return output_txt