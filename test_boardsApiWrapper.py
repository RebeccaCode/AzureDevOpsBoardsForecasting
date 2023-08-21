from constants import *
import logging
import custom_logger
from unittest import TestCase, main
from boardsApiWrapper import BoardsApiWrapper
from datetime import datetime
import yaml

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
            self.logger.debug(f'iteration {iteration.get(IterationFields.Name)} capacity is {iteration.get("calculated_capacity")}')

        # with open('./logs/data_dump_iterations.yaml', 'w') as f:
        #     yaml.dump({'Iterations': iterations}, f)

        self.logger.debug('end')

    def test_get_iterations_override_capacity(self):
        self.logger.debug('start')

        iteration_capacities = {'Sprint 1': 1,
                                'Sprint 2': 2,
                                'Sprint 3': 3,
                                'Sprint 4': 5,
                                'Sprint 5': 8,
                                'Sprint 6': 13,
                                'Sprint 7': 21,
                                'Sprint 8': 34,
                                'Sprint 9': 55,
                                'Sprint 10': 89}

        iterations = self.baw.get_iterations(override_iteration_capacities=iteration_capacities)
        self.assertIsNotNone(iterations)
        self.assertGreater(len(iterations), 0, 'No iterations found!')

        for iteration in iterations:
            self.assertIsNotNone(iteration)
            self.assertIsNotNone(iteration.get(PythonCustomFields.CalculatedCapacity), 'calculated_capacity is none!')
            self.assertEqual(iteration.get(PythonCustomFields.CalculatedCapacity), iteration_capacities.get(iteration.get(IterationFields.Name)),
                             'Iteration calculated_capacity is incorrect')
            self.logger.debug(
                f'iteration {iteration.get(IterationFields.Name)} capacity is {iteration.get("calculated_capacity")}')

        self.logger.debug('end')


if __name__ == '__main__':
    main()
