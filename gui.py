import tkinter as tk #базовый для окон и тд
from tkinter import ttk, messagebox, filedialog  #для всплывающих элементов ошибок и т п
import subprocess  #для запуска внешних программ (сишного исполнителя)
import os  #для очистки временных файлов
import time  #для засечения времени

class SortApp:
    def __init__(self, root):
        self.root = root  #ссылка на главное окно
        self.root.title("Лабораторная работа: Внешняя сортировка данных")  #заголовок окна
        self.root.geometry("800x600") #размер

        # Переменные интерфейса
        self.selected_file = tk.StringVar(value="data.csv")  #выбранный файл для сортировки
        self.sort_key = tk.StringVar(value="id")  #текущий ключ сортировки
        
        self.create_widgets() #метод отрисовки интерфейса

    def create_widgets(self):
        # Панель управления файлами
        file_frame = ttk.LabelFrame(self.root, text=" 1. Исходные данные ", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)  #расстягиваем рамку по всему окну

         #кнопка генерации
        ttk.Button(file_frame, text="Сгенерировать data.csv (1+ ГБ)", command=self.run_generator).pack(side="left", padx=5)
        #кнопка выбора файла
        ttk.Button(file_frame, text="Выбрать файл вручную", command=self.choose_file).pack(side="left", padx=5)
        #текстовая метка, привязанная к имени файла
        ttk.Label(file_frame, textvariable=self.selected_file, foreground="blue", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        # Панель настроек сортировки
        sort_frame = ttk.LabelFrame(self.root, text=" 2. Управление сортировкой ", padding=10)
        sort_frame.pack(fill="x", padx=10, pady=5)


        ttk.Label(sort_frame, text="Ключ сортировки:").pack(side="left", padx=5)
        #список
        keys_cb = ttk.Combobox(sort_frame, textvariable=self.sort_key, 
                               values=["id", "marketplace", "time", "amount", "weight", "city"], 
                               state="readonly", width=15) #запрещаем писать пользователю свой текст
        keys_cb.pack(side="left", padx=5)

        #кнопки для запуска сортировки на разных модулях
        ttk.Button(sort_frame, text="Запуск C++ Sort", command=self.run_cpp_sort).pack(side="left", padx=15)
        ttk.Button(sort_frame, text="Запуск Python Sort", command=self.run_python_sort).pack(side="left", padx=5)

        #Текстовая консоль для вывода кусков файлов
        text_frame = ttk.LabelFrame(self.root, text=" Консоль управления и верификация данных ", padding=10)
        #занимаем все оставшееся место снизу окна
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)

        #отключаем автоперенос строк, если они очень длинные
        self.txt_output = tk.Text(text_frame, wrap="none", font=("Courier New", 10))
        self.txt_output.pack(fill="both", expand=True, side="left")
        
        #ползунок прокрутки + связываем ползунок и текстовое поле
        scroll_y = ttk.Scrollbar(text_frame, command=self.txt_output.yview)
        scroll_y.pack(side="right", fill="y")
        self.txt_output.config(yscrollcommand=scroll_y.set)

    #метод для вывода ообщений в наше поле
    def log(self, message):
        self.txt_output.insert(tk.END, message + "\n") #текст в конец поля 
        self.txt_output.see(tk.END) #прокручиваем ползунок вниз
        self.root.update_idletasks() #обновляем интерфейс

    #открывает проводник для выбора файлов (незнаю будет ли рабоать на windows)
    def choose_file(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file:
            self.selected_file.set(os.path.basename(file))

    #запуск модуля генератора csv
    def run_generator(self):
        self.txt_output.delete("1.0", tk.END)
        self.log("Запуск генератора данных... Пожалуйста, подождите.")
        try:
            import generate
            generate.generate_data()
            self.log("Генерация успешно завершена!")
            self.preview_file("data.csv") #первые строки для проверки
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить генератор: {e}")

    #запуск модуля сортиоовки на питоне
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

    #запуск модуля сортиовки на си +++
    def run_cpp_sort(self):
        self.txt_output.delete("1.0", tk.END)
        key = self.sort_key.get()
        self.log(f"Запуск внешней сортировки C++ по ключу [{key}]...")
        
        #определяем какой исполняемый файл windows/linux
        import platform
        if platform.system() == "Windows":
            cpp_binary = "mysort.exe"
        else:
            cpp_binary = "./mysort"

        #если нет исполяемого файла
        if not os.path.exists(cpp_binary):
            self.log(f"Ошибка: Скомпилированный файл {cpp_binary} не найден!")
            return

        start = time.perf_counter()
        # Запускаем как отдельный процессс, передавая  элементы как для терминала
        result = subprocess.run([cpp_binary, self.selected_file.get(), key], capture_output=True, text=True)
        end = time.perf_counter()
        
        #если что то выводится в консоль, то передаем это в окне
        if result.stdout:
            self.log(result.stdout)
        if result.stderr:
            self.log(f"Ошибка C++: {result.stderr}")
            
        self.log(f"C++ успешно завершил работу за {end-start:.2f} сек!")
        self.preview_file("sortedcpp.txt")

    #первые 15 строк для показательности
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
    root = tk.Tk() #базовый обьект окна
    app = SortApp(root)  #инициализируем приложение
    root.mainloop() #бесконечный цикл для работы