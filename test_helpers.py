import logging
import custom_logger
from unittest import TestCase, main
import helpers
from datetime import datetime, timedelta


class TestHelpers(TestCase):
    def setUp(self):
        self.logger = custom_logger.get_logger(__name__)

    def tearDown(self):
        pass

    def test_convert_date_time_string_to_date(self):
        self.logger.debug('start')

        now = datetime.now()
        str_now_datetime = str(now)
        str_now_date = str_now_datetime.split(' ')[0]
        converted = helpers.convert_date_time_string_to_date(str(datetime.now()),
                                                             date_format_string='%Y-%m-%d %H:%M:%S.%f')
        self.logger.debug(converted)
        self.assertEqual(str(converted), str_now_date, 'Date conversion failed')

        self.logger.debug('end')

    def test_calculate_number_of_weekdays(self):
        self.logger.debug('start')

        start_date = helpers.convert_date_time_string_to_date('2023-08-01', date_format_string='%Y-%m-%d')
        end_date = helpers.convert_date_time_string_to_date('2023-08-15', date_format_string='%Y-%m-%d')

        unexpected_result = 10
        expected_result = 11

        result = helpers.calculate_number_of_weekdays_including_begin_end(start_date, end_date)
        self.logger.debug(result)
        self.assertNotEqual(result, unexpected_result)
        self.assertEqual(result, expected_result, 'Number of weekdays did not match expected')

        self.logger.debug('end')

    def test_calculate_number_of_weekdays_excluding_end(self):
        self.logger.debug('start')

        start_date = '2023-08'
        end_date = '2023-09'

        unexpected_result = 24
        expected_result = 23

        result = helpers.calculate_number_of_weekdays_excluding_end(start_date, end_date)
        self.logger.debug(result)
        self.assertNotEqual(result, unexpected_result)
        self.assertEqual(result, expected_result, 'Number of weekdays did not match expected')

        self.logger.debug('end')


if __name__ == '__main__':
    main()
