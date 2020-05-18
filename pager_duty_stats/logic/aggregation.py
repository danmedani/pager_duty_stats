from datetime import timedelta
from enum import Enum
from datetime import timezone
from datetime import datetime
from typing import List
from typing import Dict
import copy
from typing_extensions import TypedDict
import json

from pager_duty_stats.logic.pager_duty_client import fetch_all_incidents
from pager_duty_stats.logic.incident_types import extract_incidient_type
from pager_duty_stats.logic.incident_types import ExtractionTechnique

class GroupingWindow(Enum):
	DAY = 'day'
	WEEK = 'week'

	# useful for making args human readable
	def __str__(self):
		return self.value


class AggregrateStats(TypedDict):
	total_pages: int

	per_time_of_day: Dict[str, int]
	per_service: Dict[str, int]
	error_type_counts: Dict[str, int]


class IncidentTime(Enum):
	WORK = 'work'
	SLEEP = 'sleep'
	LEISURE = 'leisure'

	# useful for making output human readable
	def __str__(self):
		return self.value


def get_fresh_aggregate_stats() -> AggregrateStats:
	return AggregrateStats(
		total_pages=0,
		per_service={},
		per_time_of_day={},
		error_type_counts={}
	)

def is_week_day(time: datetime) -> bool:
	return time.weekday() < 5

def classify_incident_time(time: datetime) -> IncidentTime:
	if time.hour < 8:
		return IncidentTime.SLEEP

	if not is_week_day(time):
		return IncidentTime.LEISURE

	return IncidentTime.WORK if time.hour < 18 else IncidentTime.LEISURE


def get_stats_by_day(
	incidents: List[Dict],
	start_date: str,
	end_date: str,
	include_time_of_day_counts: bool,
	include_incident_types: bool,
	max_incident_types: int,
	incident_type_extraction_technique: ExtractionTechnique
) -> Dict[str, AggregrateStats]:
	incidents_by_day = {}

	for incident in incidents:
		create_date_time = datetime.strptime(incident['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).astimezone(tz=None)
		create_date = str(create_date_time.date())
		if create_date not in incidents_by_day:
			incidents_by_day[create_date] = get_fresh_aggregate_stats()
		
		incidents_by_day[create_date]['total_pages'] += 1

		if incident['service']['summary'] not in incidents_by_day[create_date]['per_service']:
			incidents_by_day[create_date]['per_service'][incident['service']['summary']] = 0

		incidents_by_day[create_date]['per_service'][incident['service']['summary']] += 1

		if include_time_of_day_counts:
			incident_time_str = str(classify_incident_time(create_date_time))
			if incident_time_str not in incidents_by_day[create_date]['per_time_of_day']:
				incidents_by_day[create_date]['per_time_of_day'][incident_time_str] = 0
			incidents_by_day[create_date]['per_time_of_day'][incident_time_str] += 1

		if include_incident_types:
			incident_type = extract_incidient_type(
				incident,
				incident_type_extraction_technique
			)
			if incident_type not in incidents_by_day[create_date]['error_type_counts']:
				incidents_by_day[create_date]['error_type_counts'][incident_type] = 0
			incidents_by_day[create_date]['error_type_counts'][incident_type] += 1

	return clean_error_type_counts(
		fill_out_empty_days(
			incidents_by_day, 
			start_date, 
			end_date
		), 
		max_incident_types
	)

def get_stats(
	incidents: List[Dict],
	start_date: str,
	end_date: str,
	grouping_window: GroupingWindow,
	include_time_of_day_counts: bool,
	include_incident_types: bool,
	incident_type_extraction_technique: ExtractionTechnique,
	max_incident_types: int
):
	stats_by_day = get_stats_by_day(
		incidents,
		start_date,
		end_date,
		include_time_of_day_counts,
		include_incident_types,
		max_incident_types,
		incident_type_extraction_technique
	)

	if grouping_window == GroupingWindow.WEEK:
		return convert_day_stats_to_week_stats(stats_by_day, end_date)
	
	if grouping_window == GroupingWindow.DAY:
		return stats_by_day

	raise Exception('Grouping Window {} not recognized'.format(grouping_window))


def fill_out_empty_days(
	stats: Dict[str, AggregrateStats],
	start_date: str,
	end_date: str
) -> Dict[str, AggregrateStats]:
	current_date = datetime.strptime(start_date, '%Y-%m-%d')
	last_date = datetime.strptime(end_date, '%Y-%m-%d')

	while current_date <= last_date:
		date_str = str(current_date.date())
		if date_str not in stats:
			stats[date_str] = get_fresh_aggregate_stats()
		current_date += timedelta(days=1)
	return stats

def get_earlist_date(dates: List[str]) -> str:
	earliest_date = str(datetime.now().date())
	for date in dates:
		if date < earliest_date:
			earliest_date = date
	return earliest_date


def convert_day_stats_to_week_stats(
	stats: Dict[str, AggregrateStats],
	end_date: str
) -> Dict[str, AggregrateStats]:
	earliest_date = get_earlist_date(list(stats.keys()))
	
	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	# Skip to the first monday, ignore anything before then
	while current_date.weekday() > 0:
		current_date += timedelta(days=1)

	last_date = datetime.strptime(end_date, '%Y-%m-%d')
	week_stats: Dict[str, AggregrateStats] = {}
	running_week_stats = get_fresh_aggregate_stats()
	start_of_week = None
	while current_date <= last_date:
		date_str = str(current_date.date())

		if current_date.weekday() == 0:
			if start_of_week:
				week_stats[start_of_week] = running_week_stats
			
			running_week_stats = get_fresh_aggregate_stats()
			start_of_week = date_str

		if date_str in stats:
			running_week_stats['total_pages'] += stats[date_str]['total_pages']
			
			for incident_time, incident_count in stats[date_str]['per_time_of_day'].items():
				if incident_time not in running_week_stats['per_time_of_day']:
					running_week_stats['per_time_of_day'][incident_time] = 0
				running_week_stats['per_time_of_day'][incident_time] += incident_count			

			for service, incident_count in stats[date_str]['per_service'].items():
				if service not in running_week_stats['per_service']:
					running_week_stats['per_service'][service] = 0
				running_week_stats['per_service'][service] += incident_count

			for incident_type, incident_count in stats[date_str]['error_type_counts'].items():
				if incident_type not in running_week_stats['error_type_counts']:
					running_week_stats['error_type_counts'][incident_type] = 0
				running_week_stats['error_type_counts'][incident_type] += incident_count

		current_date += timedelta(days=1)

	return week_stats


def clean_error_type_counts(
	stats: Dict[str, AggregrateStats],
	max_incident_types: int
) -> Dict[str, AggregrateStats]:
	# removes any errors that don't happen v often
	total_error_type_counts = {}
	for _, day_stats in stats.items():
		for error_type, error_type_count in day_stats['error_type_counts'].items():
			if error_type not in total_error_type_counts:
				total_error_type_counts[error_type] = 0
			total_error_type_counts[error_type] += error_type_count

	total_error_type_counts_list = [(key, val) for key, val in total_error_type_counts.items()]
	total_error_type_counts_list_s = sorted(total_error_type_counts_list, key=lambda pair: -1 * pair[1])
	if len(total_error_type_counts_list_s) <= max_incident_types:
		# no need to hide anything
		return stats

	stats_to_keep = set(
		[incident_types for incident_types, _ in total_error_type_counts_list_s[:max_incident_types]]
	)

	new_stats = {}
	for day, _ in stats.items():
		new_stats[day] = copy.deepcopy(stats[day])
		for error_type, _ in stats[day]['error_type_counts'].items():
			if error_type not in stats_to_keep:
				if 'misc' not in new_stats[day]['error_type_counts']:
					new_stats[day]['error_type_counts']['misc'] = 0
				new_stats[day]['error_type_counts']['misc'] += stats[day]['error_type_counts'][error_type]
				del new_stats[day]['error_type_counts'][error_type]

	return new_stats


