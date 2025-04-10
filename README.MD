# SimpleOffer: твой личный телеграм-рекрутер
## 🚩 Содержание
- [✨ О проекте](#✨-о-проекте)
- [🌐 Источники вакансий](#🌐-источники-вакансий)
- [📦 Технологии](#📦-технологии)
- [🚀 Установка и запуск](#🚀-установка-и-запуск)
- [👥 Контакты](#👥-контакты)

## ✨ О проекте
### 🚀 Найди идеальную работу без лишних движений!
Забудь про бесконечный поиск работы — [SimpleOffer](https://t.me/simple_offer_bot) сделает всё за тебя! Бот анализирует вакансии с популярных сайтов и присылает только то, что соответствует твоим запросам. Настраивай фильтры и получай актуальные предложения прямо в Telegram!

### 🔥 Почему SimpleOffer?
Больше не нужно тратить часы на просмотр сотен объявлений. Бот находит вакансии по твоим критериям и отправляет их прямо в чат. Удобно, быстро, без лишнего шума!

## 🌐 Источники вакансий

Бот [SimpleOffer](https://t.me/simple_offer_bot) парсит информацию о вакансиях с различных популярных сайтов, чтобы предоставлять пользователям наиболее актуальные и свежие предложения. На данный момент поддерживаются следующие источники:

- **[hh.ru](https://hh.ru/)** — крупнейший российский портал по поиску работы.

В разработке:
- **[superjob.ru](https://www.superjob.ru/)** — популярный сайт для поиска работы и сотрудников.

В будущем планируется добавление других источников для расширения базы вакансий и улучшения качества предложений.


## 📦 Технологии

| Технология | Ссылка | Описание |
|------------|--------|----------|
| ![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) | [Python](https://www.python.org/) | Основной язык программирования |
| ![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white) | [Poetry](https://python-poetry.org/) | Управление зависимостями |
| ![Aiogram](https://img.shields.io/badge/Aiogram-0088CC?style=for-the-badge&logo=telegram&logoColor=white) | [Aiogram](https://docs.aiogram.dev/en/latest/) | Асинхронный фреймворк для работы с Telegram API |
| ![Alembic](https://img.shields.io/badge/Alembic-006400?style=for-the-badge&logo=alembic&logoColor=white) | [Alembic](https://alembic.sqlalchemy.org/en/latest/) | Управление миграциями базы данных |
| ![Loguru](https://img.shields.io/badge/Loguru-FFA500?style=for-the-badge&logo=loguru&logoColor=white) | [Loguru](https://loguru.readthedocs.io/en/stable/) | Удобный инструмент для логирования |
| ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CE412B?style=for-the-badge&logo=sqlalchemy&logoColor=white) | [SQLAlchemy](https://www.sqlalchemy.org/) | ORM для работы с базой данных |
| ![SQLite3](https://img.shields.io/badge/SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white) | [SQLite3](https://www.sqlite.org/index.html) | Основная реляционная база данных |
| ![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white) | [Redis](https://redis.io/) | Storage для бота |
| ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) | [Docker](https://www.docker.com/) | Контейнеризация для удобного развертывания |

## 🚀 Установка и запуск

### 1️⃣ Клонирование репозитория  
Скопируйте репозиторий на свой компьютер:  
```bash
git clone https://github.com/nikikorolev/simple_offer.git
cd simple_offer
```

### 2️⃣ Создание и активация виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate  # для Windows используйте `venv\Scripts\activate`
```

### 3️⃣ Установка зависимостей
Используйте Poetry для установки всех зависимостей:

```bash
poetry install
```

### 4️⃣ Настройка переменных окружения
Создайте .env файл в корневой директории и укажите в нём настройки:
```env
TOKEN = "YOUR_BOT_TOKEN"
DB_NAME = "db"
REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0
```

### 5️⃣ Запуск с помощью Docker
Для удобства работы проект уже настроен для запуска в Docker-контейнере. В директории проекта запусти

```bash
docker-compose up --build
```

## 👥 Контакты
- [Никита Королев](https://t.me/niki_korolev)