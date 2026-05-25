import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import time

class SortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа: Внешняя сортировка данных")
        self.root.geometry("800x600")

        # Переменные интерфейса
        self.selected_file = tk.StringVar(value="data.csv")
        self.sort_key = tk.StringVar(value="id")
        
        self.create_widgets()

    def create_widgets(self):
        # 1. Панель управления файлами
        file_frame = ttk.LabelFrame(self.root, text=" 1. Исходные данные ", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(file_frame, text="Сгенерировать data.csv (1+ ГБ)", command=self.run_generator).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Выбрать файл вручную", command=self.choose_file).pack(side="left", padx=5)
        ttk.Label(file_frame, textvariable=self.selected_file, foreground="blue", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        # 2. Панель настроек сортировки
        sort_frame = ttk.LabelFrame(self.root, text=" 2. Управление сортировкой ", padding=10)
        sort_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(sort_frame, text="Ключ сортировки:").pack(side="left", padx=5)
        keys_cb = ttk.Combobox(sort_frame, textvariable=self.sort_key, 
                               values=["id", "marketplace", "time", "amount", "weight", "city"], 
                               state="readonly", width=15)
        keys_cb.pack(side="left", padx=5)

        ttk.Button(sort_frame, text="Запуск C++ Sort", command=self.run_cpp_sort).pack(side="left", padx=15)
        ttk.Button(sort_frame, text="Запуск Python Sort", command=self.run_python_sort).pack(side="left", padx=5)

        # 3. Текстовая консоль для вывода кусков файлов
        text_frame = ttk.LabelFrame(self.root, text=" Консоль управления и верификация данных ", padding=10)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.txt_output = tk.Text(text_frame, wrap="none", font=("Courier New", 10))
        self.txt_output.pack(fill="both", expand=True, side="left")
        
        scroll_y = ttk.Scrollbar(text_frame, command=self.txt_output.yview)
        scroll_y.pack(side="right", fill="y")
        self.txt_output.config(yscrollcommand=scroll_y.set)

    def log(self, message):
        self.txt_output.insert(tk.END, message + "\n")
        self.txt_output.see(tk.END)
        self.root.update_idletasks()

    def choose_file(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file:
            self.selected_file.set(os.path.basename(file))

    def run_generator(self):
        self.txt_output.delete("1.0", tk.END)
        self.log("Запуск генератора данных... Пожалуйста, подождите.")
        try:
            import generate
            generate.generate_data()
            self.log("Генерация успешно завершена!")
            self.preview_file("data.csv")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить генератор: {e}")

    def run_python_sort(self):
        self.txt_output.delete("1.0", tk.END)
        key = self.sort_key.get()
        self.log(f"Запуск внешней сортировки Python по ключу [{key}]...")
        
        import external_sort
        start = time.perf_counter()
        external_sort.main(self.selected_file.get(), key)
        end = time.perf_counter()
        
        self.log(f"Python успешно завершил работу за {end-start:.2f} сек!")
        self.preview_file("sortedpy.txt")

    def run_cpp_sort(self):
        self.txt_output.delete("1.0", tk.END)
        key = self.sort_key.get()
        self.log(f"Запуск внешней сортировки C++ по ключу [{key}]...")
        
        cpp_binary = "./mysort"
        if not os.path.exists(cpp_binary):
            self.log("Ошибка: Скомпилированный файл ./mysort не найден в текущей папке!")
            return

        start = time.perf_counter()
        # Вызываем Си-бинарник, передавая аргументы командной строки
        result = subprocess.run([cpp_binary, self.selected_file.get(), key], capture_output=True, text=True)
        end = time.perf_counter()
        
        if result.stdout:
            self.log(result.stdout)
        if result.stderr:
            self.log(f"Ошибка C++: {result.stderr}")
            
        self.log(f"C++ успешно завершил работу за {end-start:.2f} сек!")
        self.preview_file("sortedcpp.txt")

    def preview_file(self, path):
        if not os.path.exists(path):
            self.log(f"Файл {path} не найден для предварительного просмотра.")
            return
        
        self.log(f"\nПРОВЕРКА (Первые 15 строк файла {path}):")
        self.log("-" * 70)
        try:
            with open(path, "r", encoding="utf-8") as f:
                for _ in range(15):
                    line = f.readline()
                    if not line: break
                    self.log(line.strip())
        except Exception as e:
            self.log(f"Ошибка чтения файла: {e}")
        self.log("-" * 70)

if __name__ == "__main__":
    root = tk.Tk()
    app = SortApp(root)
    root.mainloop()