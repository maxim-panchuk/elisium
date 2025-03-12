#!/bin/bash

#docker-compose up --build -d

docker build -t panchesco13/elisium:latest .

docker run -e ELEVEN_LABS_API_KEY=sk_36012bf04dbaab46a31ff7c8c2d887ce31b08cd6d5182369 \
  -v $(pwd)/voice:/app/voice \
  -v $(pwd)/video:/app/video \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/tmp:/app/tmp \
  -v $(pwd)/music:/app/music \
  -v $(pwd)/transcriptions:/app/transcriptions \
  -p 8080:8080 \
  panchesco13/elisium:latest

echo "Контейнеры запущены в фоновом режиме"
echo "Для просмотра логов используйте: docker-compose logs -f"
echo "Приложение доступно по адресу: http://localhost:8080"