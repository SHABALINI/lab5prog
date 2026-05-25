import csv
import heapq
import os
import time

# Функция преобразует элементы строки к нужным типам данных для правильного сравнения
def cast_row(row):
    return [
        int(row[0]),       # id
        row[1],            # marketplace
        int(row[2]),       # order_time (Unix Timestamp)
        float(row[3]),     # order_amount
        int(row[4]),       # order_weight
        row[5]             # delivery_city
    ]

# Словарь, который связывает имя ключа с индексом колонки в CSV
KEY_INDEXES = {
    "id": 0,
    "marketplace": 1,
    "time": 2,
    "amount": 3,
    "weight": 4,
    "city": 5
}

#
def split_file(input_path, sort_key):
    print("Python Фаза 1: Разбиение большого файла на куски...")
    key_idx = KEY_INDEXES[sort_key]
    file_count = 0
    chunk = []
    MAX_ROWS = 200000 # 200тысяч строк

    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # Пропускаем заголовок

        for row in reader:
            if row:
                chunk.append(cast_row(row))
            
            # Если набрали чанк — сортируем и сбрасываем на диск
            if len(chunk) >= MAX_ROWS:
                # Сортируем по индексу выбранного ключа
                chunk.sort(key=lambda x: x[key_idx])
                
                temp_name = f"py_temp_{file_count}.txt"
                with open(temp_name, mode='w', newline='', encoding='utf-8') as temp_f:
                    writer = csv.writer(temp_f)
                    writer.writerows(chunk)
                
                print(f"Создан временный файл: {temp_name}")
                file_count += 1
                chunk = []

        # Не забываем дописать остатки файла
        if chunk:
            chunk.sort(key=lambda x: x[key_idx])
            temp_name = f"py_temp_{file_count}.txt"
            with open(temp_name, mode='w', newline='', encoding='utf-8') as temp_f:
                writer = csv.writer(temp_f)
                writer.writerows(chunk)
            file_count += 1

    return file_count


#
def merge_files(file_count, output_path, sort_key):
    print(f"Python Фаза 2: Слияние {file_count} файлов...")
    key_idx = KEY_INDEXES[sort_key]
    
    # 1. Открываем все временные файлы одновременно
    opened_files = [open(f"py_temp_{i}.txt", mode='r', encoding='utf-8') for i in range(file_count)]
    # Создаем csv-ридеры для каждого файла
    readers = [csv.reader(f) for f in opened_files]

    with open(output_path, mode='w', newline='', encoding='utf-8') as out_f:
        writer = csv.writer(out_f)
        # Записываем заголовок
        writer.writerow(["id", "marketplace", "order_time", "order_amount", "order_weight", "delivery_city"])

        # heapq.merge берет итераторы ридеров, приводит строки к нужным типам через cast_row
        # и сливает их по выбранному ключу. lambda помогает ему понять, по какому полю сравнивать.
        merged_stream = heapq.merge(*readers, key=lambda x: cast_row(x)[key_idx])
        
        # Записываем отсортированный поток в итоговый файл
        writer.writerows(merged_stream)

    # 2. Закрываем и удаляем временные файлы
    for f in opened_files:
        f.close()
    
    for i in range(file_count):
        os.remove(f"py_temp_{i}.txt")
    print("Все временные файлы Python удалены.")

def main(input_file, sort_key):
    start_total = time.perf_counter()
    
    # Фаза 1
    start_split = time.perf_counter()
    files_created = split_file(input_file, sort_key)
    end_split = time.perf_counter()
    
    # Фаза 2
    start_merge = time.perf_counter()
    merge_files(files_created, "sortedpy.txt", sort_key)
    end_merge = time.perf_counter()
    
    print("\n========================================")
    print("СОРТИРОВКА PYTHON ЗАВЕРШЕНА!")
    print(f"Время разбиения: {end_split - start_split:.2f} сек")
    print(f"Время слияния:   {end_merge - start_merge:.2f} sec")
    print(f"Общее время Python: {end_merge - start_total:.2f} сек")
    print("========================================")

if __name__ == "__main__":
    # Для теста из терминала: python3 external_sort.py data.csv city
    import sys
    if len(sys.argv) < 3:
        print("Использование: python3 external_sort.py <файл> <ключ: id|amount|time|weight|marketplace|city>")
    else:
        main(sys.argv[1], sys.argv[2])