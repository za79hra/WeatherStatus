import requests
import redis
from celery import Celery
from celery.schedules import crontab

app = Celery('weather_status', backend='redis://localhost', broker='redis://localhost:6002/0')

url = 'https://api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}'
OPEN_WEATHER_API_KEY = '435744b930e3d41b754c08cedd23c364'

@app.task
def get_weather_status(city: str) -> str:
    con = redis.StrictRedis(host='localhost', port=6002, db=0, decode_responses=True, charset='utf-8')
    city_temp = con.get(f"temp_{city}")
    if city_temp is not None:
        return f"{city}: {round(float(city_temp), 2)}C"
    try:
        response = requests.get(
            url=f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_API_KEY}'
        )
        kelvin_temp = response.json()['main']['temp']
        city_temp = kelvin_temp - 273.15 
        con.set(city, city_temp, ex=60)
        return f"{city}: {round(float(city_temp), 2)}C"
    except requests.exceptions.RequestException as exc:
        return f'Request Exception: {exc}'
    except Exception as exc:
        return f'Error: {exc}'

app.conf.beat_schedule = {
    'get_weather_for_cities': {
        'task': 'weather_status.get_weather_for_cities',
        'schedule': crontab(minute='*'),
    },
}

@app.task
def get_weather_for_cities():
    cities = ["Tehran", "Shiraz", "Mashhad", "Qom", "Isfahan", "Ardabil", "Hamedan", "Yazd", "Tabriz", "Zavareh"]
    for city in cities:
        get_weather_status.delay(city)


