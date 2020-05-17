from datetime import timedelta
from enum import Enum
from datetime import timezone
from datetime import datetime
import sys
from typing import List
from typing import Dict
from typing_extensions import TypedDict
import json
import requests
from functools import lru_cache

HIGH_URGENCY_TEAM = 'P289YKV'
LOW_URGENCY_TEAM = 'PJQKKBU'
FETCH_LIMIT = 100
PD_API = 'https://api.pagerduty.com/incidents'
YC_HIGH_URGENCY = 'Yelp Connect CRITICAL Urgency'
START_FOUR_DAY_WORK_WEEK = datetime.strptime('2020-04-20', '%Y-%m-%d').replace(tzinfo=timezone.utc)

@lru_cache(maxsize=1)
def get_api_key() -> str:
	with open(".api_key", "r") as api_key_file:
		return api_key_file.readlines()[0].rstrip('\n')

def get_windowed_incidents(teams: List[str], limit: int, offset: int) -> List[Dict]:
	headers = {
		'Authorization': 'Token token={api_key}'.format(api_key=get_api_key()),
		'Content-Type': 'application/json',
		'Accept': 'application/json',
		'From': 'dmedani@yelp.com'
	}
	params = {
		'service_ids[]': teams,
		'date_range': 'all',
		'limit': limit,
		'offset': offset
	}
	r = requests.get(PD_API, headers=headers, params=params)
	return r.json()['incidents']

def fetch_all_incidents(offset: int) -> List[Dict]:
	all_incidents = []
	while True:
		incidents = get_windowed_incidents(
			teams=[HIGH_URGENCY_TEAM, LOW_URGENCY_TEAM],
			limit=FETCH_LIMIT,
			offset=offset
		)
		if len(incidents) == 0:
			break
		all_incidents += incidents
		offset += FETCH_LIMIT

	return all_incidents


class DayStatistics(TypedDict):
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


def get_stats_by_day(incidents: List[Dict]) -> Dict[str, DayStatistics]:
	incidents_by_day = {}

	for incident in incidents:
		create_date_time = datetime.strptime(incident['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).astimezone(tz=None)
		create_date = str(create_date_time.date())
		if create_date not in incidents_by_day:
			incidents_by_day[create_date] = DayStatistics(
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

	return incidents_by_day

def get_earlist_date(dates: List[str]) -> str:
	earliest_date = str(datetime.now().date())
	for date in dates:
		if date < earliest_date:
			earliest_date = date
	return earliest_date

def fill_in_missing_stats(stats: Dict[str, DayStatistics]) -> None:
	earliest_date = get_earlist_date(stats.keys())

	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date <= datetime.now():
		date_str = str(current_date.date())
		if date_str not in stats:
			stats[date_str] = DayStatistics(
				total_pages=0,
				low_urgency=0,
				high_urgency=0,
				work_hour=0,
				leisure_hour=0,
				sleep_hour=0
			)

		current_date += timedelta(days=1)

def print_stats_csv(stats: Dict[str, DayStatistics]) -> None:
	print('{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
		'Date',
		'Total Pages',
		'Low Urgency',
		'High Urgency',
		'Work Hour Pages',
		'Leisure Hour Pages',
		'Wake up Pages'
	))

	earliest_date = get_earlist_date(stats.keys())

	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date <= datetime.now():
		date_str = str(current_date.date())
		print('{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
			date_str, 
			stats[date_str]['total_pages'],
			stats[date_str]['low_urgency'],
			stats[date_str]['high_urgency'],
			stats[date_str]['work_hour'],
			stats[date_str]['leisure_hour'],
			stats[date_str]['sleep_hour']
		))
		current_date += timedelta(days=1)


offset = int(sys.argv[1])

incidents = fetch_all_incidents(offset)
stats = get_stats_by_day(incidents)
fill_in_missing_stats(stats)

print_stats_csv(stats)


