import sys
from typing import List
from typing import Dict
import json
import requests
from functools import lru_cache

HIGH_URGENCY_TEAM = 'P289YKV'
LOW_URGENCY_TEAM = 'PJQKKBU'
FETCH_LIMIT = 100
PD_API = 'https://api.pagerduty.com/incidents'

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

offset = int(sys.argv[1])

incidents = fetch_all_incidents(offset)
print(len(incidents))


