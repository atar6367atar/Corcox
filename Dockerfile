FROM python:3.10-slim

WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Python paketlerini yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir python-telegram-bot==13.15

# Uygulama dosyalarını kopyala
COPY . .

# Bot token'ı environment variable olarak alınacak
ENV TELEGRAM_BOT_TOKEN=""

# Bot'u başlat
CMD ["python", "main.py"]
