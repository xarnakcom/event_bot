# получение погоды с OpenWeatherMap
import aiohttp
from config import WEATHER_TOKEN

async def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_TOKEN,  # Заменить в .env
        "units": "metric",
        "lang": "ru"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            try:
                temp = round(data["main"]["temp"])
                desc = data["weather"][0]["description"]
                return f"{temp}°C, {desc}"
            except:
                return "Погода не найдена"
