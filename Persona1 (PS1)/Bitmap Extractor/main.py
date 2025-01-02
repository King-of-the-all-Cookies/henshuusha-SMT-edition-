import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
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
    global file_path, image, tk_image, zoom_level
    file_path = filedialog.askopenfilename(title="Выберите файл", filetypes=[("All Files", "*.*")])
    if file_path:
        file_label.config(text=f"Выбранный файл: {file_path.split('/')[-1]}")
        try:
            # Проверка расширения
            if not file_path.lower().endswith('.bin'):
                messagebox.showerror("Ошибка", "Выберите файл с расширением .bin или .BIN")
                return

            width = int(width_entry.get())
            mode = mode_var.get()
            image = interpret_as_bitmap(file_path, width, mode)
            zoom_level = 1.0
            display_image()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при обработке файла: {e}")
    else:
        file_label.config(text="Файл не выбран")

def reload_image():
    global image, tk_image
    if file_path:
        try:
            width = int(width_entry.get())
            mode = mode_var.get()
            image = interpret_as_bitmap(file_path, width, mode)
            display_image()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при перезагрузке изображения: {e}")

def display_image():
    global tk_image
    if image:
        zoomed_image = image.resize((int(image.width * zoom_level), int(image.height * zoom_level)), Image.NEAREST)
        tk_image = ImageTk.PhotoImage(zoomed_image)
        canvas.config(scrollregion=(0, 0, zoomed_image.width, zoomed_image.height))
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)

def toggle_pixel(event):
    global image
    x = int(canvas.canvasx(event.x) / zoom_level)
    y = int(canvas.canvasy(event.y) / zoom_level)
    if 0 <= x < image.width and 0 <= y < image.height:
        current_color = image.getpixel((x, y))
        new_color = 255 - current_color  # Инвертирование цвета
        image.putpixel((x, y), new_color)
        display_image()

def save_image():
    save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if save_path:
        image.save(save_path)
        messagebox.showinfo("Успех", f"Изображение сохранено как {save_path}")

def save_to_bin():
    save_path = filedialog.asksaveasfilename(defaultextension=".bin",
                                             filetypes=[("BIN files", "*.bin"), ("All files", "*.*")])
    if save_path:
        width, height = image.size
        pixels = np.array(image.convert('L')).flatten()
        if mode_var.get() == '1bit':
            bits = ''.join(str(int(p > 127)) for p in pixels)
            byte_array = bytearray(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
        elif mode_var.get() == '8bit':
            byte_array = bytearray(pixels)
        with open(save_path, 'wb') as file:
            file.write(byte_array)
        messagebox.showinfo("Успех", f"Данные сохранены в {save_path}")

def open_table_window():
    if not image:
        messagebox.showerror("Ошибка", "Сначала откройте изображение.")
        return

    table_window = tk.Toplevel(root)
    table_window.title("Таблица пикселей")

    table_frame = tk.Frame(table_window)
    table_frame.pack(fill=tk.BOTH, expand=True)

    columns = simpledialog.askinteger("Настройка таблицы", "Введите количество столбцов:", initialvalue=16)
    if not columns:
        columns = 16

    tree = ttk.Treeview(table_frame, columns=[f"col{i}" for i in range(columns)], show="headings")
    for i in range(columns):
        tree.heading(f"col{i}", text=f"Столбец {i+1}")
        tree.column(f"col{i}", width=50, anchor='center')

    scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(fill=tk.BOTH, expand=True)

    pixels = np.array(image.convert('L'))
    rows = pixels.shape[0]
    cols = pixels.shape[1]

    for row in range(rows):
        values = []
        for col in range(columns):
            if col < cols:
                values.append(pixels[row, col])
            else:
                values.append('')
        tree.insert('', tk.END, values=values)

def zoom(event):
    global zoom_level
    if event.delta > 0:
        zoom_level *= 1.1
    else:
        zoom_level /= 1.1
    display_image()

# Function to bind Ctrl + R for reloading the image
def bind_hot_reload(event):
    reload_image()

root = tk.Tk()
root.title("Редактор битмап изображений")

file_path = ""
image = None
tk_image = None
zoom_level = 1.0

file_label = tk.Label(root, text="Файл не выбран")
file_label.pack(pady=5)

open_button = tk.Button(root, text="Открыть файл", command=open_file)
open_button.pack(pady=5)

width_label = tk.Label(root, text="Ширина изображения (px):")
width_label.pack(pady=5)

width_entry = tk.Entry(root)
width_entry.insert(0, "128")
width_entry.pack(pady=5)

mode_label = tk.Label(root, text="Режим:")
mode_label.pack(pady=5)

# Выбор режима: 1 бит (черно-белый) или 8 бит (оттенки серого)
mode_var = tk.StringVar(value="1bit")
mode_1bit = tk.Radiobutton(root, text="1 бит (Ч/Б)", variable=mode_var, value="1bit")
mode_8bit = tk.Radiobutton(root, text="8 бит (Оттенки серого)", variable=mode_var, value="8bit")
mode_1bit.pack()
mode_8bit.pack()

# Кнопка для открытия окна с таблицей пикселей
table_button = tk.Button(root, text="Открыть таблицу пикселей", command=open_table_window)
table_button.pack(pady=5)

# Кнопка для сохранения изображения в формате PNG
save_button = tk.Button(root, text="Сохранить изображение", command=save_image)
save_button.pack(pady=5)

# Кнопка для сохранения данных в бинарный файл
save_bin_button = tk.Button(root, text="Сохранить в BIN файл", command=save_to_bin)
save_bin_button.pack(pady=5)

# Кнопка для перезагрузки изображения
reload_button = tk.Button(root, text="Перезагрузить изображение", command=reload_image)
reload_button.pack(pady=5)

# Создание холста для отображения изображения с полосами прокрутки
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(canvas_frame, bg="white")
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_y = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
canvas.config(yscrollcommand=scrollbar_y.set)

scrollbar_x = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
canvas.config(xscrollcommand=scrollbar_x.set)

# Привязка событий для изменения масштаба и переключения пикселей
canvas.bind("<MouseWheel>", zoom)
canvas.bind("<Button-1>", toggle_pixel)

# Привязка события для перезагрузки изображения с помощью Ctrl + R
root.bind('<Control-r>', bind_hot_reload)

# Запуск основного цикла приложения
root.mainloop()
