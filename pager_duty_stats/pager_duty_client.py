import requests
from functools import lru_cache
from typing import Dict
from typing import List

PD_API = 'https://api.pagerduty.com/incidents'
HIGH_URGENCY_TEAM = 'P289YKV'
LOW_URGENCY_TEAM = 'PJQKKBU'
FETCH_LIMIT = 100
API_KEY_FILE = '.api_key'

@lru_cache(maxsize=1)
def get_api_key() -> str:
	with open(API_KEY_FILE, 'r') as file:
		return file.readlines()[0].rstrip('\n')

def fetch_incidents_with_limit(teams: List[str], limit: int, offset: int) -> List[Dict]:
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
		incidents = fetch_incidents_with_limit(
			teams=[HIGH_URGENCY_TEAM, LOW_URGENCY_TEAM],
			limit=FETCH_LIMIT,
			offset=offset
		)
		if len(incidents) == 0:
			break
		all_incidents += incidents
		offset += FETCH_LIMIT

	return all_incidents
