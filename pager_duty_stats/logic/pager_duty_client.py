import requests
from typing import Optional
from datetime import timedelta
from datetime import datetime
from typing import Dict
from typing import List

"""
Useful reference: https://developer.pagerduty.com/api-reference/
"""

PAGER_DUTY_API = 'https://api.pagerduty.com/incidents'
FETCH_LIMIT = 100

def fetch_incident_chunk(
	pd_api_key: str,
	service_ids: List[str],
	start_date: str,
	end_date: str,
	limit: int, 
	offset: int
) -> List[Dict]:
	headers = {
		'Authorization': 'Token token={api_key}'.format(api_key=pd_api_key),
		'Content-Type': 'application/json',
		'Accept': 'application/json',
		'From': 'dmedani@yelp.com'
	}
	params = {
		'service_ids[]': service_ids,
		'since': start_date,
		'until': end_date,
		'limit': str(limit),
		'offset': str(offset)
	}
	r = requests.get(PAGER_DUTY_API, headers=headers, params=params)

	if r.status_code == 400:
		raise Exception('400 from PagerDuty. Make sure you have legit service_ids specified')
	if r.status_code == 404:
		raise Exception('404 from PagerDuty. Double check your api key')
	
	return r.json()['incidents']

def fetch_all_incidents(
	pd_api_key: str,
	service_ids: List[str],
	start_date: str,
	end_date: str
) -> List[Dict]:
	all_incidents = []

	# pagerduty api defaults to exclusive end-date (it uses 00:00 of the date). add a day to compensate
	end_date_plus_one = str((datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).date())

	offset = 0
	while True:
		incidents = fetch_incident_chunk(
			pd_api_key=pd_api_key,
			service_ids=service_ids,
			start_date=start_date,
			end_date=end_date_plus_one,
			limit=FETCH_LIMIT,
			offset=offset
		)
		if len(incidents) == 0:
			break
		all_incidents += incidents
		offset += FETCH_LIMIT

	return all_incidents
