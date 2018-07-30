import datetime
import pytz

from django.http import JsonResponse, Http404

from . import openweather
from .log import logger

VALID_DATATYPES = [
    "summary",
    "temperature",
    "pressure",
    "humidity"
]


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

    if data["status"] == "success":
        if not data_type == "summary":
            # take off all other measurements except the ones we are
            # looking for
            partial_data = data[data_type]

            # also fill in status and timestamp for consistency
            partial_data["status"] = "success"
            partial_data["timestamp"] = data["timestamp"]

            data = partial_data

    return JsonResponse(data)
