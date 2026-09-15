FROM python:3.9-slim

WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Директория для постоянного хранения данных.
# На хостинге сюда нужно примонтировать persistent volume, иначе при редеплое
# файл данных сотрётся вместе с эфемерной файловой системой контейнера.
RUN mkdir -p /app/data
ENV DATA_FILE=/app/data/hypotheses_data.json
VOLUME ["/app/data"]

# Экспортируем порт (relaxdev.ru обычно использует 5000 или переменную окружения PORT)
EXPOSE 5000

# Запускаем приложение через gunicorn.
# ВАЖНО: 1 worker, так как данные хранятся в памяти одного процесса;
# при нескольких worker'ах каждый держит свою копию и затирает файл другого.
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-5000}", "--workers", "1", "--timeout", "120", "app:app"]
