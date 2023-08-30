from constants import *
import custom_logger
from boardsApiWrapper import BoardsApiWrapper
from customWorkItemProcessor import CustomWorkItemsProcessor
from unittest import TestCase, main


class TestCustomWorkItemsProcessor(TestCase):
    def setUp(self):
        self.cwip = CustomWorkItemsProcessor()
        self.baw = BoardsApiWrapper()
        self.logger = custom_logger.get_logger(__name__)

    def tearDown(self):
        pass

    def test_calculate_work_item_remaining_effort(self):
        self.logger.debug('start')

        item_details = self.baw.get_work_item_details_in_batch()

        test_pairs = [[WorkItemTypes.Task, None],
                      [WorkItemTypes.PBI, WorkItemTypes.Task],
                      [WorkItemTypes.Bug, WorkItemTypes.Task],
                      [WorkItemTypes.Feature, [WorkItemTypes.PBI, WorkItemTypes.Bug]],
                      [WorkItemTypes.Epic, WorkItemTypes.Feature]]

        for test_pair in test_pairs:
            self.cwip.append_calculated_work_item_remaining_effort(item_details, work_item_type=test_pair[0],
                                                                   work_item_child_type=test_pair[1])
            self.assertIsNotNone(item_details)
            for item in [x for x in item_details if
                         x.get(WorkItemFields.WorkItemType) == test_pair[0]]:
                self.assertIsNotNone(item)
                self.assertGreater(item.get(PythonCustomFields.RemainingWork), 0,
                                   'Remaining Work not greater than 0')
                self.logger.debug(
                    f'{test_pair[0]} {item.get(WorkItemFields.Title)} remaining work is {item.get(PythonCustomFields.RemainingWork)}')

        # with open('./logs/data_dump_workitems.yaml', 'w') as f:
        #     yaml.dump({'WorkItems': item_details}, f)

        self.logger.debug('end')


if __name__ == '__main__':
    main()
