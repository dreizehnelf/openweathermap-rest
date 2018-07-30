from rest_framework import serializers

from . import openweather


class CelsiusForecastSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return openweather.serialize_forecast(
            obj,
            use_fahrenheit=False
        )


class FahrenheitForecastSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return openweather.serialize_forecast(
            obj,
            use_fahrenheit=True
        )


class ErrorSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return openweather.serialize_error(str(obj))


class PartialSerializer(serializers.BaseSerializer):

    DATA_TYPE = None

    def to_representation(self, obj):

        if self.DATA_TYPE and obj["status"] == "success":

            # take off all other measurements except the ones we are
            # looking for
            partial_data = obj[self.DATA_TYPE]

            # also fill in status and timestamp for consistency
            partial_data["status"] = "success"
            partial_data["timestamp"] = obj["timestamp"]

            return partial_data

        else:
            return obj


class TemperaturePartialSerializer(PartialSerializer):
    DATA_TYPE = "temperature"


class PressurePartialSerializer(PartialSerializer):
    DATA_TYPE = "pressure"


class HumidityPartialSerializer(PartialSerializer):
    DATA_TYPE = "humidity"
