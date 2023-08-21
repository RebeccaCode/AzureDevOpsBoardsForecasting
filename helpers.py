from datetime import datetime, date
import numpy


def convert_date_time_string_to_date(date_time_string, date_format_string='%Y-%m-%dT%H:%M:%SZ'):
    if date_time_string is None:
        return None
    result = datetime.strptime(date_time_string, date_format_string).date()
    return result

def calculate_number_of_weekdays_including_begin_end(begin_date, end_date):
    result = numpy.busday_count(begin_date, end_date)
    if result > -1:
        result += 1
    return result.item()

def calculate_number_of_weekdays_excluding_end(begin_date, end_date):
    result = numpy.busday_count(begin_date, end_date)
    return result