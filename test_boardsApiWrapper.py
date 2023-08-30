from constants import *
import custom_logger
from unittest import TestCase, main
from boardsApiWrapper import BoardsApiWrapper
from datetime import datetime


class TestBoardsApiWrapper(TestCase):
    def setUp(self):
        self.baw = BoardsApiWrapper()
        self.logger = custom_logger.get_logger(__name__)

    def tearDown(self):
        pass

    def test_get_all_work_item_ids(self):
        self.logger.debug('start')

        id_list = self.baw.get_all_work_item_ids()
        self.logger.debug(id_list)
        self.assertGreater(len(id_list), 0, 'id_list size is not greater than 0')

        self.logger.debug('end')

    def test_get_work_item_details_in_batch(self):
        self.logger.debug('start')

        id_list = self.baw.get_all_work_item_ids()
        details_list = self.baw.get_work_item_details_in_batch(work_item_ids=id_list)
        self.logger.debug(details_list)
        self.assertEqual(len(details_list), len(id_list), 'details_list size not equal to id_list size')

        self.logger.debug('end')

    def test_get_iterations(self):
        self.logger.debug('start')

        iterations = self.baw.get_iterations()
        self.assertIsNotNone(iterations)
        self.assertGreater(len(iterations), 0, 'No iterations found!')

        for iteration in iterations:
            self.assertIsNotNone(iteration)

            self.assertIsNotNone(iteration.get(PythonCustomFields.CalculatedCapacity), 'calculated_capacity is none!')
            self.logger.debug(
                f'iteration {iteration.get(IterationFields.Name)} capacity is {iteration.get("calculated_capacity")}')

        # with open('./logs/data_dump_iterations.yaml', 'w') as f:
        #     yaml.dump({'Iterations': iterations}, f)

        self.logger.debug('end')

    def test_get_iterations_override_capacity(self):
        self.logger.debug('start')

        iteration_capacities = {'Sprint 1': 1 * 10,
                                'Sprint 2': 2 * 10,
                                'Sprint 3': 3 * 10,
                                'Sprint 4': 5 * 10,
                                'Sprint 5': 8 * 10,
                                'Sprint 6': 13 * 10,
                                'Sprint 7': 21 * 10,
                                'Sprint 8': 34 * 10,
                                'Sprint 9': 55 * 10,
                                'Sprint 10': 89 * 10}

        iterations = self.baw.get_iterations(override_iteration_capacities=iteration_capacities)
        self.assertIsNotNone(iterations)
        self.assertGreater(len(iterations), 0, 'No iterations found!')

        for iteration in iterations:
            self.assertIsNotNone(iteration)
            self.assertIsNotNone(iteration.get(PythonCustomFields.CalculatedCapacity), 'calculated_capacity is none!')
            self.assertEqual(iteration.get(PythonCustomFields.CalculatedCapacity),
                             iteration_capacities.get(iteration.get(IterationFields.Name)),
                             'Iteration calculated_capacity is incorrect')
            self.logger.debug(
                f'iteration {iteration.get(IterationFields.Name)} capacity is {iteration.get("calculated_capacity")}')

        self.logger.debug('end')
    def test_convert_date_time_string_to_date(self):
        self.logger.debug('start')

        now = datetime.now()
        str_now_datetime = str(now)
        str_now_date = str_now_datetime.split(' ')[0]
        converted = self.baw.__convert_date_time_string_to_date__(str(datetime.now()),
                                                             date_format_string='%Y-%m-%d %H:%M:%S.%f')
        self.logger.debug(converted)
        self.assertEqual(str(converted), str_now_date, 'Date conversion failed')

        self.logger.debug('end')

    def test_calculate_number_of_weekdays(self):
        self.logger.debug('start')

        start_date = self.baw.__convert_date_time_string_to_date__('2023-08-01', date_format_string='%Y-%m-%d')
        end_date = self.baw.__convert_date_time_string_to_date__('2023-08-15', date_format_string='%Y-%m-%d')

        unexpected_result = 10
        expected_result = 11

        result = self.baw.__calculate_number_of_weekdays_including_begin_end__(start_date, end_date)
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

        result = self.baw.__calculate_number_of_weekdays_excluding_end__(start_date, end_date)
        self.logger.debug(result)
        self.assertNotEqual(result, unexpected_result)
        self.assertEqual(result, expected_result, 'Number of weekdays did not match expected')

        self.logger.debug('end')


if __name__ == '__main__':
    main()
