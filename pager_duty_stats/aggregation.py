from datetime import timedelta
from enum import Enum
from datetime import timezone
from datetime import datetime
from typing import List
from typing import Dict
from typing_extensions import TypedDict
import json

from pager_duty_stats.pager_duty_client import fetch_all_incidents

YC_HIGH_URGENCY = 'Yelp Connect CRITICAL Urgency'
START_FOUR_DAY_WORK_WEEK = datetime.strptime('2020-04-20', '%Y-%m-%d').replace(tzinfo=timezone.utc)

class AggregrateStats(TypedDict):
	total_pages: int
	
	low_urgency: int
	high_urgency: int

	work_hour: int
	leisure_hour: int
	sleep_hour: int


class IncidentTime(Enum):
	WORK = 1
	SLEEP = 2
	LEISURE = 3


def is_high_urgency(incident: Dict) -> bool:
	return incident['service']['summary'] == YC_HIGH_URGENCY

def is_week_day(time: datetime) -> bool:
	if time < START_FOUR_DAY_WORK_WEEK:
		return time.weekday() < 5
	else:
		return time.weekday() < 4

def classify_incident_time(time: datetime) -> IncidentTime:
	if time.hour < 8:
		return IncidentTime.SLEEP

	if not is_week_day(time):
		return IncidentTime.LEISURE

	return IncidentTime.WORK if time.hour < 18 else IncidentTime.LEISURE


def get_stats_by_day(incidents: List[Dict]) -> Dict[str, AggregrateStats]:
	incidents_by_day = {}

	for incident in incidents:
		create_date_time = datetime.strptime(incident['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).astimezone(tz=None)
		create_date = str(create_date_time.date())
		if create_date not in incidents_by_day:
			incidents_by_day[create_date] = AggregrateStats(
				total_pages=0,
				low_urgency=0,
				high_urgency=0,
				work_hour=0,
				leisure_hour=0,
				sleep_hour=0
			)
		
		incidents_by_day[create_date]['total_pages'] += 1

		if is_high_urgency(incident):
			incidents_by_day[create_date]['high_urgency'] += 1

			incident_time = classify_incident_time(create_date_time)

			if incident_time == IncidentTime.WORK:
				incidents_by_day[create_date]['work_hour'] += 1
			elif incident_time == IncidentTime.SLEEP:
				incidents_by_day[create_date]['sleep_hour'] += 1
			else:
				incidents_by_day[create_date]['leisure_hour'] += 1
		else:
			# Low Urgency incidents only page during work hours
			incidents_by_day[create_date]['low_urgency'] += 1
			incidents_by_day[create_date]['work_hour'] += 1

	return incidents_by_day


def get_stats_by_week(incidents: List[Dict]) -> Dict[str, AggregrateStats]:
	return convert_day_stats_to_week_stats(
		get_stats_by_day(
			incidents
		)
	)

def get_earlist_date(dates: List[str]) -> str:
	earliest_date = str(datetime.now().date())
	for date in dates:
		if date < earliest_date:
			earliest_date = date
	return earliest_date


def convert_day_stats_to_week_stats(stats: Dict[str, AggregrateStats]) -> Dict[str, AggregrateStats]:
	earliest_date = get_earlist_date(stats.keys())
	
	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date.weekday() > 0:
		current_date += timedelta(days=1)

	week_stats = {}
	running_week_stats = None
	start_of_week = None
	while current_date <= datetime.now():
		date_str = str(current_date.date())

		if current_date.weekday() == 0:
			if running_week_stats:
				week_stats[start_of_week] = running_week_stats
			
			running_week_stats = AggregrateStats(
				total_pages=0,
				low_urgency=0,
				high_urgency=0,
				work_hour=0,
				leisure_hour=0,
				sleep_hour=0
			)
			start_of_week = date_str

		if date_str in stats:
			running_week_stats['total_pages'] += stats[date_str]['total_pages']
			running_week_stats['low_urgency'] += stats[date_str]['low_urgency']
			running_week_stats['high_urgency'] += stats[date_str]['high_urgency']
			running_week_stats['work_hour'] += stats[date_str]['work_hour']
			running_week_stats['leisure_hour'] += stats[date_str]['leisure_hour']
			running_week_stats['sleep_hour'] += stats[date_str]['sleep_hour']

		current_date += timedelta(days=1)

	return week_stats

