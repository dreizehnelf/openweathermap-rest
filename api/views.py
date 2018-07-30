import datetime
import pytz

from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import openweather, serializers
from .log import logger

DATATYPE_SUMMARY = "summary"
DATATYPE_TEMPERATURE = "temperature"
DATATYPE_PRESSURE = "pressure"
DATATYPE_HUMIDITY = "humidity"

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


@api_view(['GET'])
def weather(request, data_type, location, date, time):

    if data_type not in VALID_DATATYPES:
        raise Http404

    logger.debug(
        "Searching for {} on {} @ {}".format(
            location,
            date,
            time
        )
    )

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

        data = serializers.CelsiusForecastSerializer(forecast).data

        if not data_type == DATATYPE_SUMMARY:
            PartialSerializer = PARTIAL_SERIALIZERS.get(data_type)
            data = PartialSerializer(data).data

    except Exception as e:
        data = serializers.ErrorSerializer(e).data

    return Response(data)
