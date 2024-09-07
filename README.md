FLASK-NGINX-POSTGRES-PGADMIN на базе docker-compose

Описание: Простое web-приложение на Flask - Парсинг HH.RU с сохранением информации в БД Postrgesql.
          Имеется возможность добавления информации вручную.
          Управление базой данных можно осуществлять с помощью PgAdmin.
          Проект возможно запустить локально через файл: app/main.py
          В проекте созданы Dockerfiles и docker-compose.yml для развертывания и запуска с помощью docker-compose.

В проекте использованы технологии:

- Docker
- Compose
- Flask
- Gunicorn
- PostgreSQL
- pgamin
- nginx (reverse proxy)


Запуск приложения
- Склонировать приложение с github;
- Собрать контейнер командой: docker-compose build;
- Запустить контейнер командой: docker-compose up;
- Инициализировать базу данных Postgresql командой - docker exec flask --app main create-db.

Web-приложение будет доступно по адресу: http://127.0.0.1:5000

Доступ к Postgres:
URL: localhost:5432
Username: postgres
Password: postgres

Доступ к PgAdmin:
URL: http://127.0.0.1:5555
E-mail: root@gmail.com
Password: admin123

Подключение к Postgres из PgAdmin
Host name/address: postgres
Port: 5432
Maintenance DB: my_db
Password: postgres



