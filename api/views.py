import datetime
import pytz

from django.http import Http404

from rest_framework.decorators \
    import api_view, authentication_classes, permission_classes
from rest_framework.authentication \
    import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import openweather, serializers, models
from .log import logger

DATATYPE_SUMMARY = "summary"
DATATYPE_TEMPERATURE = "temperature"
DATATYPE_PRESSURE = "pressure"
DATATYPE_HUMIDITY = "humidity"

TEMPERATURE_SCALE_CELSIUS = "c"
TEMPERATURE_SCALE_FAHRENHEIT = "f"
TEMPERATURE_SCALE_QUERY_PARAM = "temp_scale"

VALID_DATATYPES = [
    DATATYPE_SUMMARY,
    DATATYPE_TEMPERATURE,
    DATATYPE_PRESSURE,
    DATATYPE_HUMIDITY
]

PARTIAL_SERIALIZERS = {
    DATATYPE_TEMPERATURE: serializers.TemperaturePartialSerializer,
    DATATYPE_PRESSURE: serializers.PressurePartialSerializer,
    DATATYPE_HUMIDITY: serializers.HumidityPartialSerializer
}


def search(request, data_type, location, date, time):

        if data_type not in VALID_DATATYPES:
            raise Http404

        logger.debug(
            "Searching for {} on {} @ {}".format(
                location,
                date,
                time
            )
        )

        if request.query_params.get(
            TEMPERATURE_SCALE_QUERY_PARAM,
            TEMPERATURE_SCALE_CELSIUS
        ) == TEMPERATURE_SCALE_FAHRENHEIT:
            temperature_unit = models.UNIT_FAHRENHEIT
        else:
            temperature_unit = models.UNIT_CELSIUS

        try:
            forecast = openweather.get_forecast(
                location,
                pytz.UTC.localize(
                    datetime.datetime.combine(
                        date,
                        time
                    )
                ),
                auto_update=True
            )

            UnitSerializer = serializers.CelsiusForecastSerializer \
                if temperature_unit == models.UNIT_CELSIUS \
                else serializers.FahrenheitForecastSerializer

            data = UnitSerializer(forecast).data

            if not data_type == DATATYPE_SUMMARY:
                PartialSerializer = PARTIAL_SERIALIZERS.get(data_type)
                data = PartialSerializer(data).data

        except Exception as e:
            data = serializers.ErrorSerializer(e).data

        return Response(data)


@api_view(['GET'])
def weather(request, data_type, location, date, time):
    return search(request, data_type, location, date, time)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def protected_weather(*args, **kwargs):
    return search(*args, **kwargs)
