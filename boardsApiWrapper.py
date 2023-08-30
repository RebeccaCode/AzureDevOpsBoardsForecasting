import yaml

from constants import *
import custom_logger
from datetime import datetime
import json
import requests
from requests.auth import HTTPBasicAuth
import numpy


class BoardsApiWrapper:

    def __init__(self):
        with open('config.yaml', 'r') as f:
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

    def get_all_work_item_ids(self, work_item_states_to_include=None,
                              work_item_states_to_exclude=[WorkItemStates.Done]):
        self.logger.debug('start')
        result = None
        work_item_ids_url = self.api_url_template.format(method_portion='wit/wiql',
                                                         query_portion_prefaced_by_ampersand='')
        query_string = f'SELECT [{WorkItemFields.Id}] FROM workitems WHERE [{WorkItemFields.TeamProject}] = @project'

        if work_item_states_to_include and len(work_item_states_to_include) > 0:
            comma_delim = '\'' + ','.join(work_item_states_to_include) + '\''
            query_string += f' AND [{WorkItemFields.State}] IN (\{comma_delim}\)'

        if work_item_states_to_exclude and len(work_item_states_to_exclude) > 0:
            comma_delim = '\'' + ','.join(work_item_states_to_exclude) + '\''
            query_string += f' AND [{WorkItemFields.State}] NOT IN ({comma_delim})'

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

    def get_work_item_details_in_batch(self, work_item_ids=None, max_batch_size=None, work_item_fields=None,
                                       sort_by_priority=True):
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
        statuses_found = list(dict.fromkeys([x.get(WorkItemFields.State) for x in result]))
        print(f'Work Item States Found: {statuses_found}')

        if sort_by_priority:
            for item in result:
                if not item.get(WorkItemFields.BacklogPriority):
                    item[WorkItemFields.BacklogPriority] = 0
            result = sorted(result, key=lambda x: x[WorkItemFields.BacklogPriority])  # , reverse=True)

        self.logger.debug('end')
        return result

    def get_iterations(self, current=True, future=True, past=False, override_iteration_capacities={}):
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

        past_current_future = self.__separate_iterations_by_past_current_future__(parsed_first_call.get('value'))
        process_these_iterations = []
        if current:
            process_these_iterations.extend(past_current_future.get('current'))
        if future:
            process_these_iterations.extend(past_current_future.get('future'))
        if past:
            process_these_iterations.extend(past_current_future.get('past'))

        for item in process_these_iterations:
            query = self.api_url_template.format(method_portion=f'work/teamsettings/iterations/{item.get("id")}',
                                                 query_portion_prefaced_by_ampersand='')
            response = requests.get(query, auth=self.basic_auth)

            if response.status_code != 200:
                self.logger.error(f'Failed getting iteration {item}')
                self.logger.error(response.reason)
                raise (Exception(response.reason))

            parsed_iteration = json.loads(response.content)
            parsed_iteration[IterationFields.StartDate] = self.__convert_date_time_string_to_date__(
                parsed_iteration.get('attributes').get(IterationFields.StartDate),
                date_format_string=self.api_date_format_string)
            parsed_iteration[IterationFields.FinishDate] = self.__convert_date_time_string_to_date__(
                parsed_iteration.get('attributes').get(IterationFields.FinishDate),
                date_format_string=self.api_date_format_string)

            if override_iteration_capacities and len(override_iteration_capacities) > 0:
                parsed_iteration[PythonCustomFields.CalculatedCapacity] = override_iteration_capacities.get(
                    parsed_iteration.get(IterationFields.Name))

            else:
                self.__append_calculated_iteration_capacity__(parsed_iteration)

            # TODO handle current,future,true
            result.append(parsed_iteration)

        self.logger.debug('end')
        return result

    def __append_calculated_iteration_capacity__(self, iteration):
        self.logger.debug('start')
        number_weekdays = self.__calculate_number_of_weekdays_including_begin_end__(
            iteration.get(IterationFields.StartDate),
            iteration.get(IterationFields.FinishDate))

        team_iteration_capacity_url = self.api_url_template.format(
            method_portion=f'work/teamsettings/iterations/{iteration.get(IterationFields.Id)}/capacities',
            query_portion_prefaced_by_ampersand='')

        team_days_off = self.__calculate_number_of_team_days_off__(iteration)

        total_team_capacity = self.__calculate_total_iteration_team_capacity__(iteration, number_weekdays,
                                                                               team_days_off)

        iteration[PythonCustomFields.CalculatedCapacity] = total_team_capacity
        self.logger.debug(f'iteration {iteration.get(IterationFields.Name)} capacity is {total_team_capacity}')

        self.logger.debug('end')

    def __calculate_total_iteration_team_capacity__(self, iteration, number_weekdays, team_days_off):
        team_iteration_capacity_url = iteration.get('_links').get('capacity').get('href')
        response = requests.get(team_iteration_capacity_url, auth=self.basic_auth)
        if response.status_code != 200:
            self.logger.error(response.reason)
            raise (Exception(response.reason))
        parsed = json.loads(response.content)
        total_team_capacity = 0
        for team_member in parsed.get('teamMembers'):
            daily_capacity = team_member.get('activities')[0].get('capacityPerDay')
            days_off = 0
            for date_range in team_member.get('daysOff'):
                startDate = self.__convert_date_time_string_to_date__(date_range.get('start'),
                                                                      date_format_string=self.api_date_format_string)
                finishDate = self.__convert_date_time_string_to_date__(date_range.get('end'),
                                                                       date_format_string=self.api_date_format_string)
                days_off += self.__calculate_number_of_weekdays_including_begin_end__(startDate, finishDate)
            days_available = number_weekdays - days_off - team_days_off
            capacity = days_available * daily_capacity
            total_team_capacity += capacity
        return total_team_capacity

    def __calculate_number_of_team_days_off__(self, iteration):
        team_iteration_days_off_url = iteration.get('_links').get('teamDaysOff').get('href')
        response = requests.get(team_iteration_days_off_url, auth=self.basic_auth)
        if response.status_code != 200:
            self.logger.error(response.reason)
            raise (Exception(response.reason))
        parsed = json.loads(response.content)
        days_off = 0
        for time_range in parsed.get('daysOff'):
            startDate = self.__convert_date_time_string_to_date__(time_range.get('start'),
                                                                  date_format_string=self.api_date_format_string)
            finishDate = self.__convert_date_time_string_to_date__(time_range.get('end'),
                                                                   date_format_string=self.api_date_format_string)
            days_off += self.__calculate_number_of_weekdays_including_begin_end__(startDate, finishDate)
        return days_off

    def __convert_date_time_string_to_date__(self, date_time_string, date_format_string='%Y-%m-%dT%H:%M:%SZ'):
        if date_time_string is None:
            return None
        result = datetime.strptime(date_time_string, date_format_string).date()
        return result

    def __calculate_number_of_weekdays_including_begin_end__(self, begin_date, end_date):
        result = numpy.busday_count(begin_date, end_date)
        if result > -1:
            result += 1
        return result.item()

    def __calculate_number_of_weekdays_excluding_end__(self, begin_date, end_date):
        result = numpy.busday_count(begin_date, end_date)
        return result

    def __separate_iterations_by_past_current_future__(self, iteration_list):
        result = {'past': [], 'current': [], 'future': []}
        now = datetime.date(datetime.now())

        for iteration in iteration_list:
            if iteration.get('attributes') and iteration.get('attributes').get(IterationFields.StartDate):
                start_date = self.__convert_date_time_string_to_date__(
                    iteration.get('attributes').get(IterationFields.StartDate))
                end_date = self.__convert_date_time_string_to_date__(
                    iteration.get('attributes').get(IterationFields.FinishDate))
            else:
                start_date = self.__convert_date_time_string_to_date__(iteration.get(IterationFields.StartDate))
                end_date = self.__convert_date_time_string_to_date__(iteration.get(IterationFields.FinishDate))

            if now >= start_date and now <= end_date:
                result.get('current').append(iteration)
            elif now <= start_date:
                result.get('future').append(iteration)
            elif now >= end_date:
                result.get('past').append(iteration)

        return result
