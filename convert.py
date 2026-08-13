from pydub import AudioSegment
import argparse
import os


def mp3_to_wav(input_path, output_path, target_sr = 16000):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(target_sr).set_channels(1)
    audio.export(output_path, format = "wav")
    return output_path

def split_wav(wav_path, chunk_lenght_ms = 60000, out_dir = "chunks"):
    os.makesdirs(out_dir, exist_ok = True)
    audio = AudioSegment.from_wav(wav_path)
    duration_ms = len(audio)
    chunks = []
    
    for i in range(0, duration_ms, chunk_lenght_ms):
        chunk = audio[i: i + chunk_lenght_ms]
        chunk_name = os.path.join(out_dir, f"chunk_{i//1000}_{(i + chunk_lenght_ms)//1000}.wav")
        chunk.export(chunk_name, format = "wav")
        chunk.append(chunk_name)
    
    return chunks
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Convert mp3 to wav and split into chunks")
    parser.add_argument("input", help = "Input mp3 file")
    parser.add_argument("--wav", help = "Output wav file", default = "output.wav")
    parser.add_argument("--chunk_ms", type = int, help = "Chunk lenght is ms", default = 60000)
    args = parser.parse_args()
    
    wav = mp3_to_wav(args.input, args.wav)
    print("WAV saved:", wav)
    chunks = split_wav(wav, chunk_length_ms = args.chunk_ms)
    print("Chunks: ", chunks)
    