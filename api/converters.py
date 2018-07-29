import datetime


class DateConverter:
    regex = '[0-9]{8}'
    FORMAT = "%Y%m%d"

    def to_python(self, value):
        """Convert a given URL value to a proper python date object.

        :param value: A date string in the format YYYYMMDD
        :return: A date instance representing the supplied date
        """
        dt = datetime.datetime.strptime(value, self.FORMAT)
        return dt.date()

    def to_url(self, value):
        """Convert a given date value to URL representation.

        :param value: A date or datetime instance
        :return: A string representation in the format
                 DateConverter.FORMAT
        """
        return value.strftime(self.FORMAT)


class TimeConverter:
    regex = '[0-9]{4}'
    FORMAT = "%H%M"

    def to_python(self, value):
        """Convert a given URL value to a proper python time object.

        :param value: A time string in the format YYYYMMDD
        :return: A date instance representing the supplied date
        """
        dt = datetime.datetime.strptime(value, self.FORMAT)
        return dt.time()

    def to_url(self, value):
        """Convert a given time value to URL representation.

        :param value: A time or datetime instance
        :return: A string representation in the format
                 TimeConverter.FORMAT
        """
        return value.strftime(self.FORMAT)
