#!/bin/bash

# Создаем необходимые директории
mkdir -p uploads/images
mkdir -p uploads/videos

# Запускаем сервер с Gunicorn
gunicorn --workers=4 --bind=0.0.0.0:8080 wsgi:app 