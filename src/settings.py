import os
from loguru import logger
from dotenv import load_dotenv


load_dotenv()

# Настройки бота
TOKEN = os.getenv("TOKEN")

# Настройки redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Настройки sqlite3
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"sqlite+aiosqlite:///../data/{DB_NAME}.sqlite3"


# Настройки loguru
LOG_FILE_PATH = os.path.join(os.getcwd(), "logs/bot.log")
LOG_FORMAT = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
LOG_LEVEL = "INFO"
LOG_ROTATION = "150 MB"
logger.add(LOG_FILE_PATH,
           format=LOG_FORMAT,
           level=LOG_LEVEL,
           rotation=LOG_ROTATION,
           backtrace=True,
           diagnose=True)
