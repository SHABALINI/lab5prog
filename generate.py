import csv
import random
import os
import time

# --- НАСТРОЙКИ ---
FILE_NAME = "data.csv"
TARGET_SIZE_GB = 1.05 #размер файла  
CHUNK_SIZE = 50000     # Пачка строк, которая копится в памяти перед записью

# Названия маркетплейсов (9 штук)
MARKETPLACES = [
    "ozon", "wildberries", "Яндекс.маркет", "Aliexpress", 
    "Магнит_маркет", "Мегамаркет", "Авито", "Lamoda", "Poizon"
]

# 30 городов России
CITIES = [
    "Киров", "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань",
    "Нижний Новгород", "Красноярск", "Челябинск", "Самара", "Уфа",
    "Ростов-на-Дону", "Краснодар", "Воронеж", "Пермь",
    "Волгоград", "Саратов", "Тюмень", "Тольятти", "Барнаул",
    "Махачкала", "Ижевск", "Хабаровск", "Ульяновск", "Иркутск",
    "Владивосток", "Ярославль", "Севастополь", "Ставрополь", "Курск"
]

def generate_data():
    print(f"Запуск генератора. Целевой файл: {FILE_NAME}")
    start_time = time.perf_counter()#начинаем отсчет, чтобы потом посмотреть сколько времени файл генерировался
    
    current_id = 1
    bytes_written = 0
    #gb > byte
    target_bytes = TARGET_SIZE_GB * 1024 * 1024 * 1024

    #перевод для unix Timestamp
    START_TIMESTAMP = 1735680000  #1 января 2025
    END_TIMESTAMP = 1767225600    #1 января 2026

    # Открываем файл в режиме записи w с кодировкой utf-8
    with open(FILE_NAME, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        #заголовки столбцов
        writer.writerow(["id", "marketplace", "order_time", "order_amount", "order_weight", "delivery_city"])
        
        chunk = [] #сюда собираем строки для отправки на диск
        
        # Запускаем цикл генерации
        while bytes_written < target_bytes: #работает пока не будет нужного размера (1 гб)
            #МАРКЕТПЛЕЙСЫ
            mkt = random.choice(MARKETPLACES)
            #города
            city = random.choice(CITIES)
            #время от 2025 до 2026
            order_time = random.randint(START_TIMESTAMP, END_TIMESTAMP)
            #цена от 50 до 150 000 рублей
            amount = round(random.uniform(50.0, 150000.0), 2)
            #вес от 100 грамм до 30 кг
            weight = random.randint(100, 30000)
            
            #собираем все вместе в пачку
            chunk.append([current_id, mkt, order_time, amount, weight, city])
            current_id += 1 #повышаем id
            
            #если пачка заполнилась, то скидываем в файл
            if len(chunk) >= CHUNK_SIZE:
                writer.writerows(chunk)
                chunk = [] #очищение

                #Проверяем размер файла
                bytes_written = os.path.getsize(FILE_NAME)
                progress = (bytes_written / target_bytes) * 100
                print(f"Записано: {bytes_written / (1024*1024):.1f} МБ ({progress:.1f}%)", end='\r')
        
        #если остались строки, то дописываем их
        if chunk:
            writer.writerows(chunk)

    # 
    end_time = time.perf_counter() #фиксируем затраченное время 
    final_size_mb = os.path.getsize(FILE_NAME) / (1024 * 1024) #размер файла
    
    #для терминала
    print("\n" + "="*40)
    print(f"Готово! Тестовый файл успешно создан.")
    print(f"Итоговый размер: {final_size_mb:.2f} МБ")
    print(f"Всего сгенерировано строк: {current_id - 1}")
    print(f"Затрачено времени: {end_time - start_time:.2f} сек")
    print("="*40)

if __name__ == "__main__":
    generate_data()