import datetime
import requests

from django.conf import settings
from django.urls import reverse

UNIT_CELSIUS = "℃"
UNIT_FAHRENHEIT = "℉"
UNIT_KELVIN = "K"

def make_absolute(relative_url):
    return "{base}{relative}".format(
        base=settings.BASE_URL,
        relative=relative_url
    )

def test_weather_summary():

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOCATION = "Horley"

    dates_to_check = {
        "2018-07-18 18:00:00": {
            "description": "clear sky",
            "temperature": {
                "value": 13,
                "unit": "℃"
            },
            "pressure": 1082.25,
            "humidity": {
                "value": 58,
                "unit": "%"
            }
        }
    }

    for dt_string, data in dates_to_check.items():

        dt = datetime.datetime.strptime(dt_string, DATETIME_FORMAT)

        url = reverse(
            "weather-summary",
            kwargs={
                "location": LOCATION.lower(),
                "date": dt.date(),
                "time": dt.time()
            }
        )

        r = requests.get(make_absolute(url))

        assert r.json() == data