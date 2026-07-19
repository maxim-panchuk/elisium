#!/usr/bin/env bash

# Выполним запрос, сохраняя тело в tempfile,
# а статус-код - в переменную HTTP_CODE.
HTTP_CODE=$(curl -s \
  -o response_body \
  -w "%{http_code}" \
  -X POST http://localhost:8080/generate \
  -F "text=Тренер Райана Гарсии, Эдди Рейносо, мотивирует своего подопечного перед боем с Роландо Ромеро. На видео, опубликованном в сети, слышен голос за кадром: «Скажи, у тебя лучшая левая в мире». На что Рейносо уверенно отвечает Гарсии: «У тебя лучшая левая в мире, лучшая»." \
  -F "file1=@tmp/picha.jpeg;type=image/jpeg" \
  -F "file2=@tmp/vidos.MP4;type=video/mp4")

echo "Server returned status code: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
  # Если успех, переименуем /tmp/response_body в result_1.mp4
  mv response_body result.mp4
  echo "Video saved to result.mp4"
else
  # Иначе считаем, что там текст ошибки; выведем его в консоль
  echo "Error response from server:"
  cat response_body
fi

rm -f response_body
