# Используем Python 3.13
FROM python:3.13

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы проекта
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Копируем остальной код проекта
COPY . /app

# Создаём папку для базы данных
RUN mkdir -p /data

# Указываем команду для запуска бота
CMD ["python", "src/bot.py"]
