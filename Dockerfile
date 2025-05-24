# Используем Python 3.12
FROM python:3.12

# Установка времени
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Устанавливаем git и ssh
RUN apt-get update && apt-get install -y git openssh-client

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы проекта
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Копируем остальной код проекта
COPY . /app

# Пуш аналитики
COPY scripts/push_analytics.sh /app/scripts/push_analytics.sh
RUN chmod +x /app/scripts/push_analytics.sh

RUN mkdir -p /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

# Указываем команду для запуска бота
CMD ["/bin/bash", "-c", "python src/bot.py & scripts/push_analytics.sh & wait -n"]