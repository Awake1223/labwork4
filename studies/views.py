import json
import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Article  # Импортируем модель Article

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
    except (FileNotFoundError, json.JSONDecodeError):
        pass  # Игнорируем ошибки
    return data_list


def write_data_to_json(data_list):
    with open(JSON_FILE, 'w') as json_file:
        json.dump(data_list, json_file, indent=4)


def read_data_from_db():
    return Article.objects.all()


def index(request):
    articles = read_data_from_db()  # Получаем статьи из базы данных
    create_upload_dir()  # Создаем директорию, если ее нет
    data_list = read_data_from_json()  # Чтение данных из JSON файла

    if request.method == 'POST':
        save_to_db = request.POST.get('save_to_db') == 'on'  # Проверка флага сохранения в БД

        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            try:
                uploaded_data = json.load(uploaded_file)
                if isinstance(uploaded_data, list):
                    for item in uploaded_data:
                        if save_to_db:
                            if not Article.objects.filter(title=item['title'], author=item['author'],
                                                          year=item['year']).exists():
                                Article.objects.create(**item)  # Сохраняем в БД
                        else:
                            data_list.append(item)  # Добавляем в список для JSON
                    if not save_to_db:
                        write_data_to_json(data_list)
                else:
                    return render(request, 'index.html', {'error': "Загруженный файл должен содержать список объектов.",
                                                          'data_list': data_list,
                                                          'articles': articles})  # Передаем статьи
            except json.JSONDecodeError:
                return render(request, 'index.html',
                              {'error': "Не удалось прочитать файл JSON.", 'data_list': data_list,
                               'articles': articles})  # Передаем статьи
        else:
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
                        raise ValueError("Поле 'Название' может содержать только английские и русские буквы.")
                    if not valid_name_pattern.match(author):
                        raise ValueError("Поле 'Автор' может содержать только английские и русские буквы.")

                    new_entry = {
                        'title': title,
                        'author': author,
                        'year': year
                    }

                    if save_to_db:
                        if not Article.objects.filter(title=title, author=author, year=year).exists():
                            Article.objects.create(**new_entry)  # Сохраняем в БД
                        else:
                            return render(request, 'index.html', {'error': "Запись с такими данными уже существует.",
                                                                  'data_list': data_list,
                                                                  'articles': articles})  # Передаем статьи
                    else:
                        data_list.append(new_entry)  # Добавляем в список для JSON
                        write_data_to_json(data_list)  # Записываем в файл

                    return redirect('index')  # Перенаправление после успешной отправки формы

                except ValueError as e:
                    return render(request, 'index.html', {'error': str(e), 'data_list': data_list,
                                                          'articles': articles})  # Передаем статьи

            else:
                return render(request, 'index.html', {'error': "Заполните все поля.", 'data_list': data_list,
                                                      'articles': articles})  # Передаем статьи

    return render(request, 'index.html',
                  {'data_list': data_list, 'articles': articles})  # Объединяем данные для рендеринга


def delete_article(request, article_id):
    """Удаление статьи по ID."""
    article = get_object_or_404(Article, id=article_id)
    article.delete()
    return redirect('index')


def edit_article(request, article_id):
    """Редактирование существующей статьи."""
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        title = request.POST.get('title')
        author = request.POST.get('author')
        year = request.POST.get('year')

        if title and author and year:
            try:
                year = int(year)
                if year < 1924 or year > 2100:
                    raise ValueError("Год должен быть в пределах от 1924 до 2100.")
                if not valid_name_pattern.match(title):
                    raise ValueError("Поле 'Название' может содержать только английские и русские буквы.")
                if not valid_name_pattern.match(author):
                    raise ValueError("Поле 'Автор' может содержать только английские и русские буквы.")

                article.title = title
                article.author = author
                article.year = year
                article.save()  # Сохраняем изменения

                return redirect('index')

            except ValueError as e:
                return render(request, 'edit_article.html', {'article': article, 'error': str(e)})

        else:
            return render(request, 'edit_article.html', {'article': article, 'error': "Заполните все поля."})

    return render(request, 'edit_article.html', {'article': article})


def search_articles(request):
    """Поиск статей по текстовым полям."""
    query = request.GET.get('q', '')

    if query.strip() == '':
        return JsonResponse({'error': "Введите значение для поиска"}, status=400)

    articles = Article.objects.filter(title__icontains=query) | Article.objects.filter(author__icontains=query)

    return JsonResponse(list(articles.values()), safe=False)


