FROM python:latest

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY video/ /app/video/
COPY music/ /app/music/

COPY . .

COPY .env.docker .env

RUN mkdir -p uploads/images uploads/videos tmp voice

RUN chmod +x start_prod.sh

EXPOSE 8080

CMD ["./start_prod.sh"] 