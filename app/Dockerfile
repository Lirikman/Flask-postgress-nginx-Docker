FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt /app

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

RUN flask --app main create-db

EXPOSE 5000
