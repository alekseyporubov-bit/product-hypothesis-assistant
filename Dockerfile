FROM python:3.9-slim

WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Экспортируем порт (relaxdev.ru обычно использует 5000 или переменную окружения PORT)
EXPOSE 5000

# Запускаем приложение через gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-5000}", "--workers", "4", "--timeout", "120", "app:app"]
