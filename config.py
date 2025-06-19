# конфиг для загрузки переменных окружения
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Заменить в .env
WEATHER_TOKEN = os.getenv("OPENWEATHER_TOKEN")  # Заменить в .env
