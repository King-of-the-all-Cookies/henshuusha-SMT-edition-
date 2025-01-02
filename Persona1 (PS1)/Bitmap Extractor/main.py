import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

def interpret_as_bitmap(file_path, width, mode):
    with open(file_path, 'rb') as file:
        data = file.read()

    data = data.rstrip(b'\x00')

    if mode == '1bit':
        bits = ''.join(f"{byte:08b}" for byte in data)
        pixels = np.array([int(b) for b in bits], dtype=np.uint8)
    elif mode == '8bit':
        pixels = np.frombuffer(data, dtype=np.uint8)
    else:
        raise ValueError("Unsupported mode. Use '1bit' or '8bit'.")

    height = len(pixels) // width
    if len(pixels) % width != 0:
        pixels = pixels[:height * width]

    image_array = pixels.reshape((height, width))

    if mode == '1bit':
        image = Image.fromarray(image_array * 255, mode='L')
    elif mode == '8bit':
        image = Image.fromarray(image_array, mode='L')

    return image

def open_file():
    global file_path
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("BIN Files", "*.bin"), ("All Files", "*.*")])
    if file_path:
        file_label.config(text=f"Selected file: {file_path.split('/')[-1]}")
    else:
        file_label.config(text="No file selected")

def process_file():
    if not file_path:
        messagebox.showerror("Error", "Please select a file!")
        return

    try:
        width = int(width_entry.get())
        mode = mode_var.get()
        image = interpret_as_bitmap(file_path, width, mode)

        output_path = "output_image.png"
        image.save(output_path)
        messagebox.showinfo("Success", f"Image saved as {output_path}")
        image.show()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

root = tk.Tk()
root.title("Bitmap Extractor")

file_path = ""

file_label = tk.Label(root, text="No file selected")
file_label.pack(pady=5)

open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack(pady=5)

width_label = tk.Label(root, text="Image Width (px):")
width_label.pack(pady=5)

width_entry = tk.Entry(root)
width_entry.insert(0, "128")
width_entry.pack(pady=5)

mode_label = tk.Label(root, text="Mode:")
mode_label.pack(pady=5)

mode_var = tk.StringVar(value="1bit")
mode_1bit = tk.Radiobutton(root, text="1 bit (B/W)", variable=mode_var, value="1bit")
mode_8bit = tk.Radiobutton(root, text="8 bit (Grayscale)", variable=mode_var, value="8bit")
mode_1bit.pack()
mode_8bit.pack()

process_button = tk.Button(root, text="Process and Save", command=process_file)
process_button.pack(pady=10)

root.mainloop()
