[![.github/workflows/main.yml](https://github.com/co1omkooo/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/co1omkooo/foodgram/actions/workflows/main.yml)

# Foodgram

## Описание проекта
**Foodgram** - это веб-приложение, где пользователи могут публиковать рецепты, подписываться на любимых авторов, добавлять рецепты в избранное и формировать список покупок для выбранных рецептов.

## Стек
- Python 3.9
- Django 3.2.3
- Django REST framework 3.12.4
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

## Установка 
1. Клонируйте репозиторий на свой компьютер:

    ```bash
    git clone git@github.com:co1omkooo/foodgram.git
    ```
    ```bash
    cd foodgram
    ```

2. Создайте файл .env и заполните его своими данными. Перечень данных указан в корневой директории проекта в файле .env.example.

    ```bash
    nano .env
    ```

## Собираем Docker-образы
1.  Создаем образы. Замените username на ваш логин на DockerHub:

    ```bash
    cd frontend
    docker build -t username/foodgram_frontend .
    cd ../backend
    docker build -t username/foodgram_backend .
    cd ../nginx
    docker build -t username/foodgram_gateway . 
    ```

2. Загружаем образы на Docker Hub:

    ```bash
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    docker push username/foodgram_gateway
    ```

## Деплой на сервере
1. Подключитесь к удаленному серверу

    ```bash
    ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
    ```

2. Создайте на сервере директорию foodgram через терминал

    ```bash
    mkdir foodgram
    ```

3. Установить docker compose на сервер:
    ```bash
    sudo apt update
    ```
    ```bash
    sudo apt install curl
    ```
    ```bash
    curl -fSL https://get.docker.com -o get-docker.sh
    ```
    ```bash
    sudo sh ./get-docker.sh
    ```
    ```bash    
    sudo apt-get install docker-compose-plugin
    ```

4. В директорию foodgram/ скопируйте файлы docker-compose.production.yml и .env:

    ```bash
    scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
    ```
    * ath_to_SSH — путь к файлу с SSH-ключом;
    * SSH_name — имя файла с SSH-ключом (без расширения);
    * username — ваше имя пользователя на сервере;
    * server_ip — IP вашего сервера.
    
    
    Есть и другой вариант: создайте на сервере пустой файл docker-compose.production.yml и с помощью редактора nano добавьте в него содержимое из локального docker-compose.production.yml. 

5. Запустите docker compose в режиме демона:

    ```bash
    sudo docker compose -f docker-compose.production.yml up -d
    ```

6. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:

    ```bash
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
    ```

7. На сервере в редакторе nano откройте конфиг Nginx:

    ```bash
    sudo nano /etc/nginx/sites-enabled/default
    ```

8. Измените настройки location в секции server:

    ```bash
    server {
        listen 80;
        server_name <your.domain.com>;

        location / {
            proxy_set_header Host $http_host;        
            proxy_pass http://127.0.0.1:7000;
            client_max_body_size 5M;
            
        }
    }
    ```

9. Проверьте работоспособность конфига Nginx:

    ```bash
    sudo nginx -t
    ```
    Если ответ в терминале такой, значит, ошибок нет:
    ```bash
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
    ```

10. Перезапускаем Nginx
    ```bash
    sudo nginx -s reload
    ```

## Настройка CI/CD
Настроить запуск проекта Foodgram в контейнерах и CI/CD с помощью GitHub Actions
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

1. Файл workflow уже написан. Он находится в директории

    ```bash
    foodgram/.github/workflows/main.yml
    ```

2. Для адаптации его на своем сервере добавьте секреты в GitHub Actions:

    ```bash
    DOCKER_USERNAME                # имя пользователя в DockerHub
    DOCKER_PASSWORD                # пароль пользователя в DockerHub
    HOST                           # ip_address сервера
    USER                           # имя пользователя
    SSH_KEY                        # приватный ssh-ключ
    SSH_PASSPHRASE                 # кодовая фраза (пароль) для ssh-ключа

    TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
    TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
    ```

## Автор
[Shevchenko Demid](https://github.com/co1omkooo)