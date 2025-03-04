# Используем Python 3.12
FROM python:3.12
RUN apt-get update && apt-get install -y ffmpeg

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 5000
EXPOSE 5000

# Запускаем сервер Flask
CMD ["python", "app.py"]
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
