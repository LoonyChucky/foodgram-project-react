Foodgram

Foodgram - продуктовый помощник с книгой кулинарных рецептов. 
Публикуйте свои рецепты, сохраняйте в избранное. 
Доступен для скачивания список покупок для выбранных рецептов(формат txt). 
Подписывайтесь на любимых авторов.

Проект доступен по адресу: https://kirfoodgram.servebeer.com

Документация к API: https://kirfoodgram.servebeer.com/api/docs/

В документации описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа.

Запуск проекта на локальной машине (убедитесь, что на ПК есть все необходимое ПО - см.Технологии):

1. Клонировать репозиторий
2. Создаем и активируем виртуальное окружение: python3 -m venv venv source /venv/bin/activate (source /venv/Scripts/activate - для Windows) python -m pip install --upgrade pip
3. Устанавливаем зависимости из requirements.txt: pip install -r requirements.txt
4. В корне проекта создаем файл .env и заполняем своими данными по аналогии с env.example
5. Перейти в папку infra. Создать и запустить контейнеры Docker: docker-compose -f docker-compose.yml up -d
6. Создайте миграции: sudo docker compose -f docker-compose.yml exec backend python manage.py makemigrations
7. Мигрируйте: sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
8. Загрузите список ингредиентов и тегов: sudo docker compose -f docker-compose.yml exec backend python manage.py loaddata
9. соберите статику: sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic --no-input
10. скопируйте статику бэкенда в том стратики: sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /static/static/
11. создайте супер пользователя для входа в панель администрирования: sudo docker compose -f docker-compose.yml exec backend python manage.py createsuperuser

Проект будет доступен по локальному адресу: 127.0 0.1:9090 или localhost:9090
Документация api: http://localhost/api/docs/

Для использования публичных образов автора на локальной машине - используйте файл  docker-compose.local.production.yml

Для размещения на удаленном сервере(убедитесь, что на сервере есть все необходимое ПО - см.Технологии):
1. создать в корневой директории папку foodgram для проекта
2. скопировать в папку foodgram файл docker-compose.production.yml
3. создать в папке foodgram файл .env и заполняем своими данными по аналогии с env.example
4. настроить Ваш серверный nginx на переадресцию запросов для проекта на внутренний адрес 127.0 0.1:9090
5. В папке foodgram выполнить команды указанные в пп.5-11, указанные выше

Для авторизации в API используются токены.
Получить токен можно по адресу: /api/auth/token/login

Примеры запросов:

1. Получение списка пользователей /api/users/

{
    "count": 123,
    "next": "http://foodgram.example.org/api/users/?page=4",
    "previous": "http://foodgram.example.org/api/users/?page=2",
    "results": [
        {
            "email": "user@example.com",
            "id": 0,
            "username": "string",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "is_subscribed": false
        }
    ]
}

2. Получение списка рецептов /api/recipes/

{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}

3. Получение списка покупок /api/recipes/download_shopping_cart/

Технологии:
Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL

Автор:
Кирилл Ларцев 
loonychucky@yandex.ru

(c) 2024