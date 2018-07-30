import datetime
import pytz

from django.http import Http404

import coreapi
import coreschema

from rest_framework.decorators \
    import api_view, authentication_classes, permission_classes, schema
from rest_framework.authentication \
    import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema

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


weather_schema = ManualSchema(fields=[
    coreapi.Field(
        "data_type",
        required=True,
        location="path",
        schema=coreschema.Enum(
            ["summary", "temperature", "pressure", "humidity"],
            title="Data Type",
            description=(
                "The type of response to render. One of ['summary',"
                "'temperature','pressure','humidity']"
            )

        )
    ),
    coreapi.Field(
        "location",
        required=True,
        location="path",
        schema=coreschema.String(
            title="Location",
            description=(
                "The location the weather forecast is requested for, "
                "i.e. 'Berlin,DE'"
            )
        )
    ),
    coreapi.Field(
        "date",
        required=True,
        location="path",
        schema=coreschema.String(
            description="The date in the format YYYYMMDD"
        ),
    ),
    coreapi.Field(
        "time",
        required=True,
        location="path",
        schema=coreschema.String(
            description="The time in the format HHMM"
        ),
    ),
    coreapi.Field(
        "temp_scale",
        required=False,
        location="query",
        schema=coreschema.String(
            description=(
                "Indicator of the scale to be used for the temperature "
                "values. Possible values are 'c' for Celsius (default) or 'f' "
                "for Fahrenheit. Other values will silently be ignored and "
                "Celsius will be assumed."
            )
        ),
    )
])


def search(request, data_type, location, date, time):
    """Get the weather information for a given location, date and time
    from the openweathermap.org API. Requests will be cached locally.

    :param request: The django REST framework Request object
    :param data_type: One of ["summary", "temperature", "pressure", "humidity"]
    :param location: A string with the query of the location, i.e. Berlin,DE
    :param date: A date in the format YYYYMMDD
    :param time: A time in the format HHMM
    :return: A django REST framework Response object with the JSON
             representation of the matching forecast or error if any
    """

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
@schema(weather_schema)
def weather(request, data_type, location, date, time):
    return search(request, data_type, location, date, time)


@api_view(['GET'])
@schema(weather_schema)
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def protected_weather(*args, **kwargs):
    return search(*args, **kwargs)
