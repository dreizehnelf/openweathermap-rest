import datetime
import pytz

from django.http import JsonResponse

from . import openweather
from .log import logger


def summary(request, location, date, time):

    logger.debug(
        "Searching for {} on {} @ {}".format(
            location,
            date,
            time
        )
    )

    data = openweather.get_data(
        location,
        pytz.UTC.localize(
            datetime.datetime.combine(
                date,
                time
            )
        ),
        auto_update=True
    )

    return JsonResponse(data)
