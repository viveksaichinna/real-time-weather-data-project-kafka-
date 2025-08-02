# producer/weather_producer.py
import requests
import time
import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

API_KEY = "ec3934a2647f8edd2dddd67e2a2ea09d"
CITY = "New York"

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

while True:
    data = get_weather()
    print(f"Sending: {data['main']}")
    producer.send('weather_raw', value=data)
    time.sleep(10)  # wait 10 seconds
