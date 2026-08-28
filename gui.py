import tkinter as tk
from tkinter import filedialog, messagebox
from transcribe import transcribe_file


def choose_file():
    file_path = filedialog.askopenfilename(filetypes = [("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("All files", "*.*")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)
        
def run_transcription():
    mp3_path = entry_file.get()
    if not mp3_path:
        messagebox.showerror("Error!", "Choose a audio-file")
    
    model_size = model_var.get()
    chunk_ms = int(entry_chunk.get())
    language = entry_lang.get()
    output_txt = entry_out.get() or "transcribe.txt"
    
    try:
        transcribe_file(mp3_path, model_size = model_size, chunk_ms = chunk_ms, language = language, output_txt = output_txt)
        messagebox.showinfo("DOne!", f"Transcription was saved in {output_txt}")
        
        with open(output_txt, "r", encoding="utf-8") as f:
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, f.read())
    except Exception as e:
        messagebox.showerror("Error!", str(e))

root = tk.Tk()
root.title("Voice2Wors")

# File
tk.Label(root, text = "Audio file:").grid(row = 0, column = 0, sticky = "w", padx = 5, pady = 5)
entry_file = tk.Entry(root, width = 50)
entry_file.grid(row = 0, column = 1, padx = 5, pady = 5)
tk.Button(root, text = "Choose file...", command = choose_file).grid(row=0, column=2, padx=5, pady=5)

# Model
tk.Label(root, text = "Choose model of Whisper model for transcription: ").grid(row = 1, column = 0, sticky = "w", padx = 5, pady = 5)
model_var = tk.StringVar(value = "medium")
tk.OptionMenu(root, model_var, "tiny", "base", "small", "medium", "large").grid(row = 1, column = 1, sticky = "w", padx = 5, pady = 5)

# Chunk lenght
tk.Label(root, text = "Choose length of chunk in seconds: ").grid(row = 2, column = 0, sticky = "w", padx = 5, pady = 5)
entry_chunk = tk.Entry(root)
entry_chunk.insert(0, "60000")
entry_chunk.grid(row = 2, column = 1, sticky = "w", padx = 5, pady = 5)

# Language
tk.Label(root, text = "Specify the audio language: en, ru").grid(row = 3, column = 0, sticky = "w", padx = 5, pady = 5)
entry_lang = tk.StringVar(value = "en")
tk.OptionMenu(root, entry_lang, "en", "ru").grid(row = 3, column = 1, sticky = "w", padx = 5, pady = 5)

# File of result
tk.Label(root, text = "File of result: ").grid(row = 4, column = 0, sticky = "w", padx = 5, pady = 5)
entry_out = tk.Entry(root)
entry_out.insert(0, "transcribe.txt")
entry_out.grid(row = 4, column = 1, sticky = "w", padx = 5, pady = 5)

# Button for start
tk.Button(root, text = "Start", command = run_transcription).grid(row = 5, column = 0, columnspan = 3, pady = 10)

# Field for text
text_box = tk.Text(root, wrap = "word", width = 80, height = 20)
text_box.grid(row = 6, column = 0, columnspan = 3, padx = 10, pady = 10)

root.mainloop()