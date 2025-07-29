import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json

FILE_TYPES = {
    'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
    'Audio': ['.mp3', '.wav', '.aac'],
    'Videos': ['.mp4', '.mov', '.avi', '.mkv'],
    'Archives': ['.zip', '.rar', '.tar', '.gz'],
    'Scripts': ['.py', '.js', '.cpp', '.java', '.html', '.css'],
    'Others': []
}

UNDO_LOG_FILE = "undo_log.json"

def get_category(extension):
    for category, extensions in FILE_TYPES.items():
        if extension.lower() in extensions:
            return category
    return 'Others'

def organize_folder(path, log_text):
    if not os.path.isdir(path):
        messagebox.showerror("Error", f"{path} is not a valid directory.")
        return

    log_text.delete('1.0', tk.END)
    file_moves = []
    count = 0

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            category = get_category(ext)
            target_dir = os.path.join(path, category)
            os.makedirs(target_dir, exist_ok=True)

            new_path = os.path.join(target_dir, filename)
            shutil.move(file_path, new_path)

            file_moves.append({"from": new_path, "to": file_path})
            log_text.insert(tk.END, f"Moved: {filename} → {category}/\n")
            count += 1

    with open(UNDO_LOG_FILE, 'w') as f:
        json.dump(file_moves, f)

    messagebox.showinfo("Done", f"Organized {count} files.\nYou can undo this operation.")

def undo_last_action(log_text):
    if not os.path.exists(UNDO_LOG_FILE):
        messagebox.showinfo("Undo", "No undo log found.")
        return

    with open(UNDO_LOG_FILE, 'r') as f:
        file_moves = json.load(f)

    restored = 0
    for move in file_moves:
        if os.path.exists(move["from"]):
            os.makedirs(os.path.dirname(move["to"]), exist_ok=True)
            shutil.move(move["from"], move["to"])
            log_text.insert(tk.END, f"Restored: {os.path.basename(move['from'])}\n")
            restored += 1

    os.remove(UNDO_LOG_FILE)
    messagebox.showinfo("Undo Complete", f"Restored {restored} files.")

def browse_directory(entry):
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

app = tk.Tk()
app.title("File Organizer")
app.geometry("600x500")

style = ttk.Style()
style.theme_use("clam")

frame = tk.Frame(app)
frame.pack(pady=10)

tk.Label(frame, text="Select Folder to Organize:").grid(row=0, column=0, padx=5)
path_entry = tk.Entry(frame, width=45)
path_entry.grid(row=0, column=1, padx=5)
browse_btn = ttk.Button(frame, text="Browse", command=lambda: browse_directory(path_entry))
browse_btn.grid(row=0, column=2)

log_text = tk.Text(app, height=18, width=70)
log_text.pack(pady=10)

button_frame = tk.Frame(app)
button_frame.pack()

organize_btn = ttk.Button(button_frame, text="Organize Files", command=lambda: organize_folder(path_entry.get(), log_text))
organize_btn.grid(row=0, column=0, padx=10)

undo_btn = ttk.Button(button_frame, text="Undo Last Action", command=lambda: undo_last_action(log_text))
undo_btn.grid(row=0, column=1, padx=10)

app.mainloop()
