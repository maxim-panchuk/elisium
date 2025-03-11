#!/bin/bash

# Создаем необходимые директории
mkdir -p uploads/images
mkdir -p uploads/videos
mkdir -p tmp
mkdir -p voice

# Запускаем сервер с Gunicorn
# Используем 4 рабочих процесса и таймаут 300 секунд (5 минут) для длительных операций генерации
gunicorn --workers=4 --timeout=500 --bind=0.0.0.0:8080 wsgi:app 