import tkinter as tk
from tkinter import filedialog, messagebox
from transcribe import transcribe_file


def choose_file():
    file_path = filedialog.askopenfilename(filetypes = [("Audio files", "*.mp3, *.wav")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)
        
def run_transcriprion():
    mp3_path = entry_file.get()
    if not mp3_path:
        messagebox.showerror("Error!", "Choose a audio-file")
        

root = tk.Tk()
root.title("Voice2Wors")

# File
tk.Label(root, text = "Audio file:").pack(anchor = "w")
entry_file = tk.Entry(root, width = 50)
entry_file.pack(side = "left", padx = 5 )
tk.Button(root, text = "Choose...", command = choose_file).pack(side = "left")

# Model
tk.Label(root, text = "Choose model of Whisper (model for transcriprion:").pack(side = "bottom")
model_var = tk.StringVar(value = "small")
tk.OptionMenu(root, model_var, "tiny", "base", "small", "medium", "large").pack()

# Chunk lenght
tk.Label(root, text = "Choose length of chunk in seconds: ").pack(anchor = "w")
entry_chunk = tk.Entry(root)
entry_chunk.insert(0, "60000")
entry_chunk.pack()

# Language
tk.Label(root, text = "Language: en, ru ...").pack(anchor = "w")
entry_out = tk.Entry(root)
entry_out.insert(0, "transcribe.txt")
entry_out.pack()

# File of result
tk.Label(root, text = "File of result: ").pack(anchor = "w")
entry_out = tk.Entry(root)
entry_out.insert(0, "transcribe.txt")
entry_out.pack()

# Button for start
tk.Button(root, text = "Start", command = run_transcriprion).pack(pady = 10)

# Field for text
text_box = tk.Text(root, wrap = "word", width = 80, height = 20)
text_box.pack(padx = 10, pady = 10)

root.mainloop()