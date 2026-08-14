def mp3_to_wav(input_path, output_path, target_sr = 16000):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(target_sr).set_channels(1)
    audio.export(output_path, format = "wav")
    return output_path

def split_wav(wav_path, chunk_length_ms = 60000, out_dir = "chunks"):
    os.makedirs(out_dir, exist_ok = True)
    audio = AudioSegment.from_wav(wav_path)
    duration_ms = len(audio)
    chunks = []
    
    for i in range(0, duration_ms, chunk_length_ms):
        chunk = audio[i: i + chunk_length_ms]
        chunk_name = os.path.join(out_dir, f"chunk_{i//1000}_{(i + chunk_length_ms)//1000}.wav")
        chunk.export(chunk_name, format = "wav")
        chunks.append(chunk_name)
    
    return chunks
