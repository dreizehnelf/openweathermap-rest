import requests
import datetime
import pytz
import traceback

from django.conf import settings

from . import models
from .log import logger

# forecasts are valid for 3 hours
FORECAST_MAX_AGE = datetime.timedelta(seconds=3 * 60 * 60)

# forecasts are only available for the next 5 days
FORECAST_MAX_WINDOW = datetime.timedelta(days=5)

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

API_URL = (
    "http://api.openweathermap.org/data/2.5/forecast"
    "?q={{query}}&APPID={api_key}".format(
        api_key=settings.OPENWEATHERMAPORG_API_KEY
    )
)


def query(location):
    url = API_URL.format(query=location)
    result = requests.get(url)

    logger.debug("{} --> {}".format(url, result.text))

    # TODO: handle non 200 HTTP codes
    return result.json()


def add_forecasts(location):
    data = query(location)

    # check the response
    if data["cod"] == "200":

        city_data = data["city"]

        try:
            city = models.City.objects.get(ref=city_data["id"])

        except models.City.DoesNotExist:

            city = models.City(
                ref=city_data["id"],
                name=city_data["name"],
                latitude=city_data["coord"]["lat"],
                longitude=city_data["coord"]["lon"],
                country_code=city_data["country"]
            )

            city.save()

        try:
            search_result = models.CitySearchResult.objects.get(
                search=location,
                city=city
            )

        except models.CitySearchResult.DoesNotExist:

            search_result = models.CitySearchResult(
                search=location,
                city=city
            )

            search_result.save()

        for forecast_data in data["list"]:

            try:

                # We might have a previous forecast, so make sure, we
                # don't produce duplicates. Technically this should
                # NOT happen, but just to be save.

                timestamp = pytz.UTC.localize(
                    datetime.datetime.strptime(
                        forecast_data["dt_txt"],
                        DATETIME_FORMAT
                    )
                )

                logger.debug("Adding forecast for '{}' @ {}".format(
                    location,
                    timestamp
                ))

                try:
                    forecast = models.Forecast.objects.get(
                        city=city,
                        timestamp=timestamp
                    )

                    forecast.temperature = models.kelvin_to_celsius(
                        forecast_data["main"]["temp"]
                    )
                    forecast.pressure = forecast_data["main"]["pressure"]
                    forecast.humidity = forecast_data["main"]["humidity"]

                except models.Forecast.DoesNotExist:

                    forecast = models.Forecast(
                        city=city,
                        timestamp=timestamp,
                        description=", ".join(
                            [
                                condition["description"]
                                for condition in forecast_data["weather"]
                            ]
                        ),
                        temperature=models.kelvin_to_celsius(
                            forecast_data["main"]["temp"]
                        ),
                        pressure=forecast_data["main"]["pressure"],
                        humidity=forecast_data["main"]["humidity"]
                    )

                forecast.save()

            except ValueError:
                logger.error(traceback.format_exc())

        return city.forecasts

    else:
        # sth. went wrong
        raise RuntimeError("Error while querying data, {}.".format(
            data
        ))


def serialize_forecast(forecast, use_fahrenheit=False):
    temperature_unit = models.UNIT_FAHRENHEIT \
        if use_fahrenheit \
        else models.UNIT_CELSIUS

    temperature_value = forecast.get_temperature(unit=temperature_unit)

    return {
        "status": "success",
        "timestamp": forecast.timestamp.strftime(DATETIME_FORMAT),
        "description": forecast.description,
        "temperature": {
            "value": temperature_value,
            "unit": temperature_unit
        },
        "humidity": {
            "value": forecast.humidity,
            "unit": "%"
        },
        "pressure": {
            "value": forecast.pressure,
            "unit": "hPa"
        }
    }


def serialize_error(message):
    return {
        "status": "error",
        "message": message
    }


def filter_forecasts(forecasts, from_date, to_date):
    if not forecasts:
        return None

    # we should only get one result from the filter at max - but to be sure
    # order descending by timestamp, so the latest forecast is on top
    return forecasts \
        .filter(timestamp__range=(from_date, to_date)) \
        .order_by("-timestamp") \
        .first()


def get_data(location, timestamp, auto_update=False):
    try:

        now = datetime.datetime.now(tz=pytz.UTC)
        max_forecast = now + FORECAST_MAX_WINDOW

        if timestamp > max_forecast:
            raise ValueError("Can not get forecasts further out than 5 days.")

        # assume we don't know the location
        city = None

        # flag to ensure, we don't request the forecasts more than once per
        # invocation
        forecasts_requested = False

        # assume no available forecasts
        forecasts = []

        # see, if we know that location from previous searches
        try:
            search = models.CitySearchResult.objects.get(search=location)
            city = search.city

        except models.CitySearchResult.DoesNotExist:
            # we have not searched for that location before, so we'll trigger a
            # query to the openweather API - that way we will get a) the city
            # lookup and b) current forecast data in one API call
            pass

        if city:
            # get our forecasts
            forecasts = city.forecasts

        else:
            if timestamp >= now:
                forecasts = add_forecasts(location)
                forecasts_requested = True
            else:
                logger.debug(
                    "Timestamp {} is in the past, no reason "
                    "to query API".format(
                        timestamp.strftime(DATETIME_FORMAT)
                    )
                )

        # We now have a list of forecasts, so go and see, if we have one that
        # fits into our timeframe. Since forecasts is a proper django object
        # and not just an array, we can easily filter by timeframe.
        # We need to know, whether we do have a forecast that is at most 3
        # hours prior to the requested timestamp

        oldest_timestamp = timestamp - FORECAST_MAX_AGE

        logger.debug("DB lookup yielded {} forecasts for {}.".format(
            forecasts.count() if forecasts else 0,
            location
        ))

        # we should only get one result from the filter max - but to be sure
        # order descending by timestamp, so the latest forecast is on top
        forecast = filter_forecasts(forecasts, oldest_timestamp, timestamp)

        if not forecast:

            if auto_update:

                if timestamp > now:

                    if not forecasts_requested:

                        logger.debug(
                            "No forecasts available, but auto-update is "
                            "enabled - so requesting current forecasts from "
                            "API."
                        )

                        forecasts = add_forecasts(location)
                        forecast = filter_forecasts(
                            forecasts, oldest_timestamp, timestamp
                        )

                    else:
                        logger.debug(
                            "No forecasts available and API has already been"
                            "requested."
                        )

                else:
                    logger.debug(
                        "No forecasts available and timestamp is in the past, "
                        "so querying the API is not an option."
                    )

            else:
                logger.debug(
                    "No forecasts available, and auto-update is disabled."
                )

        if forecast:
            return serialize_forecast(forecast)
        else:
            raise RuntimeError(
                "Unfortunately there's no data for "
                "'{location}' on {timestamp}".format(
                    location=location,
                    timestamp=timestamp.strftime(DATETIME_FORMAT)
                )
            )

    except Exception as e:
        return serialize_error(str(e))
