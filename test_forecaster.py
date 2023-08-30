import yaml

import custom_logger
from unittest import TestCase, main
from forecaster import Forecaster
from customWorkItemProcessor import CustomWorkItemsProcessor
from boardsApiWrapper import BoardsApiWrapper


class TestForecaster(TestCase):
    def setUp(self):
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

        self.project = self.config.get('BoardsApiWrapper').get('Project')

        self.logger = custom_logger.get_logger(__name__)
        self.fe = Forecaster()
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

        output_path = 'logs/test.xlsx'
        self.fe.create_forecast_as_excel(self.test_workitems, self.test_iterations, output_path)

        self.logger.debug('end')


if __name__ == '__main__':
    main()
