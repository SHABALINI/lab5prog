#include <iostream>
#include <fstream> //чтение и запись файлов
#include <sstream> //парсес csv
#include <string> 
#include <vector> //для динамических массивов
#include <algorithm> //встроенная сортировка
#include <chrono> //таймер
#include <queue> //минимальная куча
#include <iomanip> //для 2 знаков после запятой
#include <cstdio> //оптимизация оперативки

// структура нашего заказа строго по сгенерированным полям
struct Order {
    long long id;
    std::string marketplace;
    long long order_time; // Unix Timestamp
    double order_amount;
    int order_weight;
    std::string delivery_city;
};

//функция для считывания данных из csv и расскладывания в структуру order
Order parseCSVLine(const std::string& line) {
    Order order;
    std::stringstream ss(line); //считываем строку в поток данных 
    std::string item; // для считывания кусочков

    //1 Читаем ID
    std::getline(ss, item, ',');//считываем, разделитель запятая
    order.id = std::stoll(item); // Конвертируем строку в long long

    // 2Читаем маркетплейс
    std::getline(ss, order.marketplace, ',');

    // 3 Читаем уремя заказа (Unix Timestamp)
    std::getline(ss, item, ',');
    order.order_time = std::stoll(item);

    // 4 Читаем сумму заказа
    std::getline(ss, item, ',');
    order.order_amount = std::stod(item); // Конвертируем строку в double

    // 5 Читаем Вес заказа
    std::getline(ss, item, ',');
    order.order_weight = std::stoi(item); // Конвертируем строку в int

    // 6 Читаем Город доставки
    std::getline(ss, order.delivery_city, ',');

    return order;
}

//функция для собирания строки обратно в csv
std::string orderToCSV(const Order& order) {
    std::stringstream ss;
    //пишем в фиксированном формате с 2 знаками после запятой
    ss << std::fixed << std::setprecision(2); 
    
    //собираем по порядку
    ss << order.id << ","
       << order.marketplace << ","
       << order.order_time << ","
       << order.order_amount << ","
       << order.order_weight << ","
       << order.delivery_city;
    return ss.str();
}

//====компараторы сравнения для сортировки======
//Сравнение по ID (от меньшего к большему)
bool compareById(const Order& a, const Order& b) {
    return a.id < b.id;
}
// Сравнение по Сумме заказа
bool compareByAmount(const Order& a, const Order& b) {
    if(a.order_amount == b.order_amount) return a.id < b.id;  //если сумма одинаковая, то по айди
    
    return a.order_amount < b.order_amount;
}
// Сравнение по Времени заказа (Unix Timestamp)
bool compareByTime(const Order& a, const Order& b) {
    if (a.order_time == b.order_time) return a.id < b.id;//Если время одинаковое, то по айди
    return a.order_time < b.order_time;
}
//сравнение по весу
bool compareByWeight(const Order& a, const Order& b) {
    if (a.order_weight == b.order_weight) return a.id < b.id; //если вес одинаковы, то по айди
    return a.order_weight < b.order_weight;
}
// Сравнение по Маркетплейсу (по алфавиту)
bool compareByMarketplace(const Order& a, const Order& b) {
    if(a.marketplace == b.marketplace) return a.id < b.id; //если одинаковые маркеты, то сортируем по id

    return a.marketplace < b.marketplace;
}
// Сравнение по Городу доставки (по алфавиту)
bool compareByCity(const Order& a, const Order& b) {
    if(a.delivery_city == b.delivery_city) return a.id < b.id; //если города равны, то сортируем по id

    return a.delivery_city < b.delivery_city;
}
//==================================================

//======== Функция разбивает большой файл на отсортированные куски========
// Возвращает количество созданных временных файлов
int splitFile(const std::string& input_path, const std::string& key) {
    std::ifstream in(input_path);//открытие файла
    if (!in.is_open()) {
        std::cerr << "Ошибка: Не удалось открыть файл " << input_path << std::endl;
        return 0;
    }

    std::string line;
    // Пропускаем самую первую строчку с заголовками (id, marketplace и тд), чтобы она не превратилась в кашу при сортировке данных
    std::getline(in, line); 

    std::vector<Order> chunk; //динамический массив, в котором будем хранить данные и парсить
    const size_t MAX_ROWS = 500000; // 500 тысяч строк 
    int file_count = 0; //счетчик данных

    std::cout << "Фаза 1: Разбиение большого файла на куски..." << std::endl;

    while (true) {
        bool is_eof = !std::getline(in, line); //читаем строку, если файл кончается то возращаем true;
        
        // Если строка не пустая, парсим её и кладем в массив
        if (!is_eof && !line.empty()) {
            chunk.push_back(parseCSVLine(line));
        }

        // Если набрали нужное кол-во строк ИЛИ файл закончился
        if (chunk.size() >= MAX_ROWS || (is_eof && !chunk.empty())) {
            
            // Выбираем компаратор сортировки в зависимости от переданного ключа
           if (key == "id") {
              file_count++;
            //chunk.shrink_to_fit(); std::sort(chunk.begin(), chunk.end(), compareById);
            std::sort(chunk.begin(), chunk.end(), compareById);
            } else if (key == "amount") {
                std::sort(chunk.begin(), chunk.end(), compareByAmount);
            } else if (key == "time") {
                std::sort(chunk.begin(), chunk.end(), compareByTime);
            } else if (key == "weight") {
                std::sort(chunk.begin(), chunk.end(), compareByWeight);
            } else if (key == "marketplace") {
                std::sort(chunk.begin(), chunk.end(), compareByMarketplace);
            } else if (key == "city") {
                std::sort(chunk.begin(), chunk.end(), compareByCity);
            } else {
                // Если передан неизвестный ключ, отсортируем по умолчанию (по ID)
                std::sort(chunk.begin(), chunk.end(), compareById);
            }

            // Записываем отсортированный кусок во временный файл
            std::string temp_name = "temp_" + std::to_string(file_count) + ".txt";
            std::ofstream out(temp_name);
            
            //пишем в файлы
            for (const auto& order : chunk) {
                out << orderToCSV(order) << "\n";
            }
            
            out.close();//закрываем файл, чтобы не засорять память
            std::cout << "Создан временный файл: " << temp_name << " (" << chunk.size() << " строк)" << std::endl;
            
            file_count++;
            chunk.clear(); // Полностью очищаем память под новый кусок
            chunk.shrink_to_fit(); //освобождаем ОЗУ смекалочка кировская
        }

        if (is_eof) break; //если прочитали файл полностью, то выходим
    }

    in.close(); //закрываем
    return file_count; // Возвращаем сколько всего файлов наплодили
}


//Теперь сливаем все файлы вместе
//структура для хранения текущего элемента слияния
struct MergeElement {
    Order order;
    int file_index;
};

// Класс-компаратор для нашей очереди
class MergeElementGreater {
    std::string key;
public:
    MergeElementGreater(std::string sort_key) : key(sort_key) {}

    bool operator()(const MergeElement& a, const MergeElement& b) const {
        if (key == "id") return a.order.id > b.order.id; //Развернули знак, так как в куче queue от макс к мин, а нам надо наоборот от мин к макс
        if (key == "amount"){
            if(a.order.order_amount == b.order.order_amount) return a.order.id > a.order.id;
            return a.order.order_amount > b.order.order_amount;
        }
        if (key == "time"){ 
            if(a.order.order_time == b.order.order_time) return a.order.id > b.order.id;
            return a.order.order_time > b.order.order_time;
        }
        if (key == "weight"){
            if(a.order.order_weight == b.order.order_weight) return a.order.id > b.order.id;
            return a.order.order_weight > b.order.order_weight;
        }
        if (key == "marketplace") {
            if(a.order.marketplace == b.order.marketplace) return a.order.id > b.order.id;
            return a.order.marketplace > b.order.marketplace;
        }
        if (key == "city") {
            if (a.order.delivery_city == b.order.delivery_city) return a.order.id > b.order.id;
            return a.order.delivery_city > b.order.delivery_city;
        }
        return a.order.id > b.order.id;
    }
};


//=============функция слияния=================
void mergeFiles(int file_count, const std::string& output_path, const std::string& key) {
    std::cout << "Фаза 2: Слияние " << file_count << " временных файлов в " << output_path << "..." << std::endl;

    //создаем массив из всех временных файлов на чтение 
    std::vector<std::ifstream> inputs(file_count);
    for (int i = 0; i < file_count; ++i) {
        std::string temp_name = "temp_" + std::to_string(i) + ".txt";
        inputs[i].open(temp_name);
    }

    //Открываем итоговый файл на запись
    std::ofstream out(output_path);
    // Пишем заголовки в новый файл
    out << "id,marketplace,order_time,order_amount,order_weight,delivery_city\n";

    // Создаем минимальную кучу (тип данных, контейнер хранения и класс компаратор)
    MergeElementGreater comparator(key);
    std::priority_queue<MergeElement, std::vector<MergeElement>, MergeElementGreater> min_heap(comparator);

    // Читаем по первой строчке из каждого файла и загружаем подходящий 
    for (int i = 0; i < file_count; ++i) {
        std::string line;
        if (std::getline(inputs[i], line) && !line.empty()) {
            MergeElement elem;
            elem.order = parseCSVLine(line); 
            elem.file_index = i; //запомнили из какого файла
            min_heap.push(elem); //кидаем в кучу
        }
    }

    // Главный цикл слияния, работает пока не опустеет куча
    long long rows_written = 0;
    while (!min_heap.empty()) {
        // Берем самый минимальный элемент из кучи (самый первы .top)
        MergeElement smallest = min_heap.top();
        min_heap.pop(); //удаляем его

        // Записываем его в итоговый файл
        out << orderToCSV(smallest.order) << "\n";
        rows_written++;
        if (rows_written % 2000000 == 0) {
            std::cout << "Записано в итоговый файл: " << rows_written << " строк..." << std::endl; //для отслеживания прогресса
        }

        // Читаем следующую строку из того же файла, откуда был этот элемент и кидаем в кучу
        std::string line;
        if (std::getline(inputs[smallest.file_index], line) && !line.empty()) {
            MergeElement next_elem;
            next_elem.order = parseCSVLine(line);
            next_elem.file_index = smallest.file_index; //тот же файл
            min_heap.push(next_elem); // Кидаем в кучу, она сама перестроится
        }
    }

    // Закрываем все файлы и удаляем временные
    out.close();
    for (int i = 0; i < file_count; ++i) {
        inputs[i].close();
        std::string temp_name = "temp_" + std::to_string(i) + ".txt";
        std::remove(temp_name.c_str()); // Удаляем(cstdio)
    }
    std::cout << "Все временные файлы удалены." << std::endl;
}

int main(int argc, char* argv[]) {
    //argc - аргументы для командной строки
    //argv - массив указателей на строки-аргументы
    if (argc < 3) { //вызываем инструкцию как пользоваться и все доступные ключи
        std::cout << "Использование: " << argv[0] << " <имя_файла.csv> <ключ: id|amount|time|weight|marketplace|city>" << std::endl;
        return 1;
    }

    std::string input_file = argv[1]; //сортируемый файл
    std::string sort_key = argv[2]; //ключ
    std::string output_file = "sortedcpp.txt"; //отсортированный файл

    // --- ФАЗА 1 ---
    auto start_split = std::chrono::high_resolution_clock::now(); //фиксируем время
    int total_temp_files = splitFile(input_file, sort_key); //пилим
    auto end_split = std::chrono::high_resolution_clock::now(); //окончание времени
    
    if (total_temp_files == 0) return 1; //для ошибки чтения

    // --- ФАЗА 2 ---
    auto start_merge = std::chrono::high_resolution_clock::now(); //фиксируем время
    mergeFiles(total_temp_files, output_file, sort_key); //собираем файлы
    auto end_merge = std::chrono::high_resolution_clock::now(); //окончание времени 

    //считаем время всех фаз и общее время
    std::chrono::duration<double> split_dur = end_split - start_split;
    std::chrono::duration<double> merge_dur = end_merge - start_merge;
    std::chrono::duration<double> total_dur = end_merge - start_split;

    //победа
    std::cout << "\n========================================" << std::endl;
    std::cout << "ПОЛНАЯ СОРТИРОВКА ЗАВЕРШЕНА" << std::endl;
    std::cout << "Время разбиения: " << split_dur.count() << " сек" << std::endl;
    std::cout << "Время слияния:   " << merge_dur.count() << " сек" << std::endl;
    std::cout << "Общее время: " << total_dur.count() << " сек" << std::endl;
    std::cout << "========================================" << std::endl;

    return 0;
}
