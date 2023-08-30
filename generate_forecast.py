import yaml
from datetime import datetime

from constants import *
import custom_logger
from forecaster import Forecaster
from customWorkItemProcessor import CustomWorkItemsProcessor
from boardsApiWrapper import BoardsApiWrapper

logger = custom_logger.get_logger('generate_forecast')
now = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
output_path = f'./forecasts/flowshare_forecast_generated_{now}.xlsx'

with open('./config.yaml', 'r') as f:
    config = yaml.safe_load(f)
baw = BoardsApiWrapper()
cwip = CustomWorkItemsProcessor()
fe = Forecaster()

iterations = baw.get_iterations()
work_item_ids = baw.get_all_work_item_ids(work_item_states_to_exclude=[WorkItemStates.Done])
work_items = baw.get_work_item_details_in_batch(work_item_ids=work_item_ids)

item_type_pairs = [[WorkItemTypes.Task, None],
                   [WorkItemTypes.PBI, WorkItemTypes.Task],
                   [WorkItemTypes.Bug, WorkItemTypes.Task],
                   [WorkItemTypes.Feature, [WorkItemTypes.PBI, WorkItemTypes.Bug]],
                   [WorkItemTypes.Epic, WorkItemTypes.Feature]]

for test_pair in item_type_pairs:
    cwip.append_calculated_work_item_remaining_effort(work_items, work_item_type=test_pair[0],
                                                           work_item_child_type=test_pair[1])

fe.create_forecast_as_excel(iteration_list=iterations, work_item_detail_list=work_items, output_path=output_path)
