import datetime
import requests

from django.conf import settings
from django.urls import reverse


def make_absolute(relative_url):
    return "{base}{relative}".format(
        base=settings.BASE_URL,
        relative=relative_url
    )


def test_weather_summary():

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOCATION = "Berlin,DE"

    dates_to_check = {
        "2018-07-18 18:00:00": {
            "message": "Unfortunately there's no data "
                       "for 'berlin,de' on 2018-07-18 18:00:00",
            "status": "error"
        },
        "2018-08-02 12:00:00": {
            "timestamp": "2018-08-02 12:00:00",
            "description": "clear sky",
            "temperature": {
                "value": 28,
                "unit": "\u2103"
            },
            "humidity": {
                "value": 69.0,
                "unit": "%"
            },
            "pressure": {
                "value": 1028.06,
                "unit": "hPa"
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
