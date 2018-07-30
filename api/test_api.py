import datetime
import requests

from django.conf import settings
from django.urls import reverse


def make_absolute(relative_url):
    return "{base}{relative}".format(
        base=settings.BASE_URL,
        relative=relative_url
    )


def test_weather():

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOCATION = "Berlin,DE"

    dates_to_check = {
        "2018-07-18 18:00:00": {
            "summary": {
                "message": "Unfortunately there's no data "
                           "for 'berlin,de' on 2018-07-18 18:00:00",
                "status": "error"
            },
            "temperature": {
                "message": "Unfortunately there's no data "
                           "for 'berlin,de' on 2018-07-18 18:00:00",
                "status": "error"
            },
            "humidity": {
                "message": "Unfortunately there's no data "
                           "for 'berlin,de' on 2018-07-18 18:00:00",
                "status": "error"
            },
            "pressure": {
                "message": "Unfortunately there's no data "
                           "for 'berlin,de' on 2018-07-18 18:00:00",
                "status": "error"
            },
            "invalid": None
        },

        "2018-08-30 18:00:00": {
            "summary": {
                "status": "error",
                "message": "Can not get forecasts further out than 5 days."
            },
            "temperature": {
                "status": "error",
                "message": "Can not get forecasts further out than 5 days."
            },
            "humidity": {
                "status": "error",
                "message": "Can not get forecasts further out than 5 days."
            },
            "pressure": {
                "status": "error",
                "message": "Can not get forecasts further out than 5 days."
            },
            "invalid": None
        },

        "2018-08-02 12:00:00": {
            "summary": {
                "status": "success",
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
            },
            "temperature": {
                "status": "success",
                "timestamp": "2018-08-02 12:00:00",
                "value": 28,
                "unit": "\u2103"
            },
            "humidity": {
                "status": "success",
                "timestamp": "2018-08-02 12:00:00",
                "value": 69.0,
                "unit": "%"
            },
            "pressure": {
                "status": "success",
                "timestamp": "2018-08-02 12:00:00",
                "value": 1028.06,
                "unit": "hPa"
            },
            "invalid": None
        }
    }

    for dt_string, data in dates_to_check.items():

        for data_type, result in data.items():

            dt = datetime.datetime.strptime(dt_string, DATETIME_FORMAT)

            url = reverse(
                "weather",
                kwargs={
                    "data_type": data_type,
                    "location": LOCATION.lower(),
                    "date": dt.date(),
                    "time": dt.time()
                }
            )

            r = requests.get(make_absolute(url))

            if result is None:
                # we expect a 404
                assert r.status_code == 404
            else:
                # otherwise we expect json data
                assert r.json() == result

            # now test the same url with the view that is using
            # authentication and make sure it's not accessible

            url = reverse(
                "protected-weather",
                kwargs={
                    "data_type": data_type,
                    "location": LOCATION.lower(),
                    "date": dt.date(),
                    "time": dt.time()
                }
            )

            r = requests.get(make_absolute(url))

            assert r.status_code == 403
