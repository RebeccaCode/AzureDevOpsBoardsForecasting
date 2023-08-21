import yaml

from constants import *
import custom_logger
import helpers
from helpers import convert_date_time_string_to_date
import json
import requests
from requests.auth import HTTPBasicAuth


class BoardsApiWrapper:

    def __init__(self, organization, project):
        self.__init__()
        self.organization = organization
        self.project = project

    def __init__(self, project):
        self.__init__()
        self.project = project

    def __init__(self):
        with open('./config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        self.logger = custom_logger.get_logger(__name__)

        self.organization = self.config.get('BoardsApiWrapper').get('Organization')
        self.project = self.config.get('BoardsApiWrapper').get('Project')

        self.email = self.config.get('BoardsApiWrapper').get('LoginEmail')
        self.azure_pat = self.config.get('BoardsApiWrapper').get('LoginPAT')
        self.basic_auth = HTTPBasicAuth(self.email, self.azure_pat)
        self.api_date_format_string = self.config.get('BoardsApiWrapper').get('APIDateFormatString')

        self.azure_service = self.config.get('BoardsApiWrapper').get('AzureService')
        self.api_version = self.config.get('BoardsApiWrapper').get('APIVersion')
        self.api_url_template = f'https://{self.azure_service}/{self.organization}/{self.project}/_apis/' \
                                + '{method_portion}/?' + f'api-version={self.api_version}' + '{query_portion_prefaced_by_ampersand}'

        self.work_item_fields = WorkItemFields.All_Fields  # + BoardsScrumWorkItemCustomFields.All_Fields
        self.max_work_item_batch_size = self.config.get('BoardsApiWrapper').get('APIMaxWorkItemBatchSize')

    def get_all_work_item_ids(self):
        self.logger.debug('start')
        result = None
        work_item_ids_url = self.api_url_template.format(method_portion='wit/wiql',
                                                         query_portion_prefaced_by_ampersand='')
        query_string = f'SELECT [{WorkItemFields.Id}] FROM workitems WHERE [{WorkItemFields.TeamProject}] = @project'
        payload = {'query': query_string}
        response = requests.post(work_item_ids_url, json=payload,
                                 auth=self.basic_auth)

        if response.status_code != 200:
            self.logger.error(response.reason)
            raise (Exception(response.reason))

        parsed = json.loads(response.content)
        work_item_ids = [x.get(IterationFields.Id) for x in parsed.get('workItems')]
        result = work_item_ids

        self.logger.debug('end')
        return result

    def get_work_item_details_in_batch(self, work_item_ids=None, max_batch_size=None, work_item_fields=None):
        self.logger.debug('start')

        if not work_item_ids or len(work_item_ids) > 0:
            work_item_ids = self.get_all_work_item_ids()

        if not work_item_fields or len(work_item_fields) > 0:
            work_item_fields = self.work_item_fields

        if not max_batch_size or max_batch_size > self.max_work_item_batch_size:
            max_batch_size = self.max_work_item_batch_size

        result = []

        azure_url_work_item_batch_url = self.api_url_template.format(method_portion='wit/workitemsbatch',
                                                                     query_portion_prefaced_by_ampersand='')

        if len(work_item_ids) > max_batch_size:
            broken_out_work_item_ids = [work_item_ids[i * max_batch_size:(i + 1) * max_batch_size] for i in
                                        range((len(work_item_ids) + max_batch_size - 1) // max_batch_size)]
        else:
            broken_out_work_item_ids = [work_item_ids]

        for index, work_item_id_list in enumerate(broken_out_work_item_ids):
            payload = {'fields': work_item_fields, 'ids': work_item_id_list}
            response = requests.post(azure_url_work_item_batch_url, json=payload, auth=self.basic_auth)

            if response.status_code != 200:
                self.logger.error(f'Failed processing position {index} of broken_out_work_item_ids')
                self.logger.error(response.reason)
                raise (Exception(response.reason))

            parsed = json.loads(response.content)
            subset = parsed.get('value')
            result.extend([x.get('fields') for x in parsed.get('value')])

        types_found = list(dict.fromkeys([x.get(WorkItemFields.WorkItemType) for x in result]))
        print(f'Work Item Types Found: {types_found}')

        self.logger.debug('end')
        return result

    def get_iterations(self, override_iteration_capacities={}):
        self.logger.debug('start')

        result = None
        iterations_query_url = self.api_url_template.format(method_portion='work/teamsettings/iterations',
                                                            query_portion_prefaced_by_ampersand='')
        response = requests.get(iterations_query_url, auth=self.basic_auth)

        if response.status_code != 200:
            self.logger.error(response.reason)
            raise (Exception(response.reason))

        result = []
        parsed_first_call = json.loads(response.content)

        for item in parsed_first_call.get('value'):
            query = self.api_url_template.format(method_portion=f'work/teamsettings/iterations/{item.get("id")}',
                                                 query_portion_prefaced_by_ampersand='')
            response = requests.get(query, auth=self.basic_auth)

            if response.status_code != 200:
                self.logger.error(f'Failed getting iteration {item}')
                self.logger.error(response.reason)
                raise (Exception(response.reason))

            parsed_iteration = json.loads(response.content)
            parsed_iteration[IterationFields.StartDate] = convert_date_time_string_to_date(
                parsed_iteration.get('attributes').get(IterationFields.StartDate),
                date_format_string=self.api_date_format_string)
            parsed_iteration[IterationFields.FinishDate] = convert_date_time_string_to_date(
                parsed_iteration.get('attributes').get(IterationFields.FinishDate),
                date_format_string=self.api_date_format_string)

            if override_iteration_capacities and len(override_iteration_capacities) > 0:
                parsed_iteration[PythonCustomFields.CalculatedCapacity] = override_iteration_capacities.get(
                    parsed_iteration.get(IterationFields.Name))

            else:
                self.__append_calculated_iteration_capacity__(parsed_iteration)

            result.append(parsed_iteration)

        self.logger.debug('end')
        return result

    def __append_calculated_iteration_capacity__(self, iteration):
        self.logger.debug('start')
        number_weekdays = helpers.calculate_number_of_weekdays_including_begin_end(
            iteration.get(IterationFields.StartDate),
            iteration.get(IterationFields.FinishDate))

        team_iteration_capacity_url = self.api_url_template.format(
            method_portion=f'work/teamsettings/iterations/{iteration.get(IterationFields.Id)}/capacities',
            query_portion_prefaced_by_ampersand='')

        response = requests.get(team_iteration_capacity_url, auth=self.basic_auth)
        if response.status_code != 200:
            self.logger.error(response.reason)
            raise (Exception(response.reason))

        parsed = json.loads(response.content)
        team_days_off = parsed.get('totalDaysOff')

        total_team_capacity = 0
        for team_member in parsed.get('teamMembers'):
            daily_capacity = team_member.get('activities')[0].get('capacityPerDay')
            days_off = 0
            for date_range in team_member.get('daysOff'):
                startDate = helpers.convert_date_time_string_to_date(date_range.get('start'),
                                                                     date_format_string=self.api_date_format_string)
                finishDate = helpers.convert_date_time_string_to_date(date_range.get('end'),
                                                                      date_format_string=self.api_date_format_string)
                days_off += helpers.calculate_number_of_weekdays_including_begin_end(startDate, finishDate)
            days_available = number_weekdays - days_off - team_days_off
            capacity = days_available * daily_capacity
            total_team_capacity += capacity

        iteration[PythonCustomFields.CalculatedCapacity] = total_team_capacity
        self.logger.debug(f'iteration {iteration.get(IterationFields.Name)} capacity is {total_team_capacity}')

        self.logger.debug('end')
