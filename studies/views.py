import json
import os
import re
from django.shortcuts import render, redirect

JSON_FILE = 'uploads/data.json'  # Укажите путь к вашему JSON файлу

valid_name_pattern = re.compile(r'^[а-яА-ЯёЁa-zA-Z0-9\s]+$')

def create_upload_dir():
    if not os.path.exists(os.path.dirname(JSON_FILE)):
        os.makedirs(os.path.dirname(JSON_FILE))

def read_data_from_json():
    data_list = []
    try:
        with open(JSON_FILE, 'r') as json_file:
            data_list = json.load(json_file)
    except FileNotFoundError:
        pass  # Игнорируем, если файл еще не существует
    except json.JSONDecodeError:
        pass  # Игнорируем, если файл пуст или поврежден
    return data_list

def write_data_to_json(data_list):
    with open(JSON_FILE, 'w') as json_file:
        json.dump(data_list, json_file, indent=4)

def index(request):
    create_upload_dir()  # Создаем директорию, если ее нет

    data_list = read_data_from_json()  # Чтение данных из JSON файла

    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        year = request.POST.get('year')

        # Проверка наличия всех данных и валидация
        if title and author and year:
            try:
                year = int(year)
                if year < 1924 or year > 2100:
                    raise ValueError("Год должен быть в пределах от 1924 до 2100.")
                if not valid_name_pattern.match(title):
                    error_message = "Поле 'Название' может содержать только английские и русские буквы."
                    return render(request, 'index.html', {'data_list': data_list, 'error': error_message})
                if not valid_name_pattern.match(author):
                    error_message = "Поле 'Автор' может содержать только английские и русские буквы."
                    return render(request, 'index.html', {'data_list': data_list, 'error': error_message})
                # Сохраняем новые данные в JSON файл
                new_entry = {
                    'title': title,
                    'author': author,
                    'year': year
                }

                # Апдейт списка и запись в файл
                data_list.append(new_entry)
                write_data_to_json(data_list)

                # Перенаправление после успешной отправки формы
                return redirect('index')

            except ValueError as e:
                return render(request, 'index.html', {'error': str(e), 'data_list': data_list})

        else:
            return render(request, 'index.html', {'error': "Заполните все поля.", 'data_list': data_list})

    return render(request, 'index.html', {'data_list': data_list})