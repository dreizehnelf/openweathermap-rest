import math

from django.db import models

KELVIN_CELSIUS_OFFSET = -273.15
UNIT_CELSIUS = "℃"
UNIT_FAHRENHEIT = "℉"


def kelvin_to_celsius(value):
    return value + KELVIN_CELSIUS_OFFSET


def celsius_to_kelvin(value):
    return value - KELVIN_CELSIUS_OFFSET


def celsius_to_fahrenheit(value):
    return value * 9 / 5 + 32


class City(models.Model):

    ref = models.IntegerField(null=True, blank=True, unique=True)
    name = models.CharField(max_length=128)
    latitude = models.FloatField()
    longitude = models.FloatField()
    country_code = models.CharField(max_length=2)

    def __str__(self):
        return u"{}, {}".format(
            self.name,
            self.country_code
        )


class CitySearchResult(models.Model):

    search = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        unique=True
    )

    city = models.ForeignKey(
        "City",
        on_delete=models.CASCADE,
        related_name="searches"
    )


class Forecast(models.Model):

    SUPPORTED_TEMPERATURE_UNITS = [
        UNIT_CELSIUS,
        UNIT_FAHRENHEIT
    ]

    city = models.ForeignKey(
        "City",
        on_delete=models.CASCADE,
        related_name="forecasts"
    )

    timestamp = models.DateTimeField()
    description = models.CharField(max_length=256)

    # we will store in Celsius, but with full float precision to allow for
    # proper conversion to Farenheit, if needed - we can pre-calculate
    # Fahrenheit and stored it as well, but for now, runtime is not that much
    # of a concern and we don't wan't to bloat the DB with redundant data if
    # not really needed.
    temperature = models.FloatField()

    pressure = models.FloatField()
    humidity = models.FloatField()

    def get_temperature(self, unit):

        if not unit or unit == UNIT_CELSIUS:
            value = self.temperature

        elif unit == UNIT_FAHRENHEIT:
            value = celsius_to_fahrenheit(self.temperature)

        else:
            raise ValueError(
                "Unit {} is not supported, please use any of {}".format(
                    self.SUPPORTED_TEMPERATURE_UNITS
                )
            )

        return math.ceil(value)
