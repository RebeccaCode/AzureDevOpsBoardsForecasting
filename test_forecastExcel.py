import yaml

from constants import *
import logging
import custom_logger
from unittest import TestCase, main
from forecastExcel import ForecastExcel
from customWorkItemProcessor import CustomWorkItemsProcessor
from boardsApiWrapper import BoardsApiWrapper
from datetime import datetime, timedelta


class TestForecastExcel(TestCase):
    def setUp(self):
        with open('./config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

        self.project = self.config.get('BoardsApiWrapper').get('Project')

        self.logger = custom_logger.get_logger(__name__)
        self.fe = ForecastExcel()
        self.cwip = CustomWorkItemsProcessor()
        self.baw = BoardsApiWrapper()

        with open('test_data.yaml', 'r') as f:
            data = yaml.safe_load(f)
            self.test_iterations = data.get(self.project).get('Iterations')
            self.test_workitems = data.get(self.project).get('WorkItems')

    def tearDown(self):
        pass

    def test_create_forecast_as_excel(self):
        self.logger.debug('start')

        self.fe.create_forecast_as_excel(self.test_workitems, self.test_iterations)

        self.logger.debug('end')


if __name__ == '__main__':
    main()
