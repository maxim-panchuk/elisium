#!/bin/bash

mkdir -p uploads/images uploads/videos tmp voice

docker-compose up --build -d

echo "Контейнеры запущены в фоновом режиме"
echo "Для просмотра логов используйте: docker-compose logs -f"
echo "Приложение доступно по адресу: http://localhost:8080" 