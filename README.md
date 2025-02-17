[![.github/workflows/main.yml](https://github.com/co1omkooo/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/co1omkooo/foodgram/actions/workflows/main.yml)

# Foodgram

## Описание проекта
**Foodgram** - это веб-приложение, где пользователи могут публиковать рецепты, подписываться на любимых авторов, добавлять рецепты в избранное и формировать список покупок для выбранных рецептов.

## Стек
- Python
- Django
- Django REST framework
- JavaScript
- Nginx
- Gunicorn
- Docker compose
- GitHub Actions

## Возможности проекта
- Публикация своих рецептов с указанием ингредиентов иописанием приготовления;
- Просмотр рецептов других пользователей с возможностью фильтрации по тегам;
- Добавление рецептов в избранное для быстрого доступа;
- Подписка на авторов и просмотр их новых рецептов в ленте подписок;
- Формирование и скачивание списка покупок, основанного на выбранных рецептах;
- Смена пароля и редактирование профиля.

## Развертывание проекта на сервере 

1. Создайте на сервере директорию foodgram через терминал 
    ```bash 
    mkdir foodgram 
    ```
2. В директорию foodgram/ скопируйте файлы docker-compose.production.yml и .env: 
    ```bash 
    scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml 
    ``` 
    * ath_to_SSH — путь к файлу с SSH-ключом; 
    * SSH_name — имя файла с SSH-ключом (без расширения); 
    * username — ваше имя пользователя на сервере; 
    * server_ip — IP вашего сервера. 

    Есть и другой вариант: создайте на сервере пустой файл docker-compose.production.yml и с помощью редактора nano добавьте в него содержимое из локального docker-compose.production.yml. 
3. Запустите Dockercompose
    ```
    sudo docker compose -f docker-compose.production.yml pull
    sudo docker compose -f docker-compose.production.yml down
    sudo docker compose -f docker-compose.production.yml up -d
    ```
4. Сделайте миграции и соберите статику
    ```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/ 
    ```

## Локальное развертывание
1. Клонируйте репозиторий 
    ```
    git clone https://github.com/co1omkooo/foodgram.git
    ```
2. Перейдите в директорию
    ```
    cd backend/
    ```
3. Примените миграции
    ```
    python manage.py migrate
    ```
4. Загрузите фикстуры
    ```
    python manage.py load_data
    ```
5. Запустите локальный сервер
    ```
    python manage.py runserver
    ```

Настроить запуск проекта Foodgram в контейнерах и CI/CD с помощью GitHub Actions
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

Изучите [фронтенд веб-приложения](http://localhost) и [спецификацию API](http://localhost/api/docs/).

## Автор
[Shevchenko Demid](https://github.com/co1omkooo)