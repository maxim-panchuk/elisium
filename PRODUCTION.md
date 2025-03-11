# Запуск Elisium в производственном режиме

## Предварительные требования

- Python 3.8 или выше
- pip
- virtualenv (опционально)

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <url-репозитория>
   cd elisium
   ```

2. Создайте и активируйте виртуальное окружение (опционально, но рекомендуется):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Linux/macOS
   venv\Scripts\activate     # Для Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Запуск в производственном режиме

### Простой запуск

Используйте скрипт `start_prod.sh`:

```bash
./start_prod.sh
```

### Ручной запуск

```bash
gunicorn --workers=4 --bind=0.0.0.0:8080 wsgi:app
```

Вы можете изменить количество рабочих процессов и порт по вашему усмотрению.

### Запуск как службы systemd (для Linux)

1. Отредактируйте файл `elisium.service`, указав правильные пути к вашему проекту.
2. Скопируйте файл в `/etc/systemd/system/`:
   ```bash
   sudo cp elisium.service /etc/systemd/system/
   ```
3. Перезагрузите демон systemd:
   ```bash
   sudo systemctl daemon-reload
   ```
4. Включите и запустите службу:
   ```bash
   sudo systemctl enable elisium
   sudo systemctl start elisium
   ```
5. Проверьте статус:
   ```bash
   sudo systemctl status elisium
   ```

## Настройка Nginx (опционально)

Для использования Nginx в качестве прокси-сервера перед Gunicorn, добавьте следующую конфигурацию в `/etc/nginx/sites-available/elisium`:

```nginx
server {
    listen 80;
    server_name ваш-домен.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Затем создайте символическую ссылку и перезапустите Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/elisium /etc/nginx/sites-enabled/
sudo systemctl restart nginx
``` 