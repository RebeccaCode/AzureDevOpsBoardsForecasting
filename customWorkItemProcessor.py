from constants import *
import yaml


class CustomWorkItemsProcessor():
    def __init__(self):
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

        self.default_effort_task = self.config.get('CustomWorkItemsProcessor').get('DefaultEffort').get(
            WorkItemTypes.Task)
        self.default_effort_pbi = self.config.get('CustomWorkItemsProcessor').get('DefaultEffort').get(
            WorkItemTypes.PBI)
        self.default_effort_bug = self.config.get('CustomWorkItemsProcessor').get('DefaultEffort').get(
            WorkItemTypes.Bug)
        self.default_effort_feature = self.config.get('CustomWorkItemsProcessor').get('DefaultEffort').get(
            WorkItemTypes.Feature)
        self.default_effort_epic = self.config.get('CustomWorkItemsProcessor').get('DefaultEffort').get(
            WorkItemTypes.Epic)
        self.default_effort_dict = {WorkItemTypes.Task: self.default_effort_task,
                                    WorkItemTypes.PBI: self.default_effort_pbi,
                                    WorkItemTypes.Feature: self.default_effort_feature,
                                    WorkItemTypes.Epic: self.default_effort_epic,
                                    WorkItemTypes.Bug: self.default_effort_bug}

    def append_calculated_work_item_remaining_effort(self, work_item_details_list,
                                                     work_item_type=WorkItemTypes.Task,
                                                     work_item_child_type=None):

        type_items = [x for x in work_item_details_list if
                      x.get(WorkItemFields.WorkItemType) == work_item_type]
        for item in type_items:
            total_effort = 0

            # if there are children, take remaining effort as sum of child remaining effort
            if work_item_child_type:
                if not isinstance(work_item_child_type, list):
                    work_item_child_type = [work_item_child_type]
                all_children = [x for x in work_item_details_list if
                                x.get(WorkItemFields.WorkItemType) in work_item_child_type and x.get(
                                    WorkItemFields.Parent) == item.get(
                                    WorkItemFields.Id)]
                if not all_children or len(all_children) == 0:
                    total_effort = self.default_effort_dict.get(work_item_type)
                else:
                    total_effort = sum(
                        [x.get(PythonCustomFields.RemainingWork) for x in all_children if
                         x.get(PythonCustomFields.RemainingWork) is not None])
            else:
                # if no children, take the first of these values in order
                for key in [PythonCustomFields.RemainingWork,
                            WorkItemFields.RemainingWork,
                            WorkItemFields.Effort]:
                    value = item.get(key)
                    if value:
                        total_effort = value
                        break

            # finally, prefer the default value if no other value was set
            if total_effort <= 0:
                total_effort = self.default_effort_dict.get(work_item_type)

            item[PythonCustomFields.RemainingWork] = total_effort
