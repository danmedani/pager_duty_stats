from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List

import requests

"""
Useful reference: https://developer.pagerduty.com/api-reference/
"""

PAGER_DUTY_API = 'https://api.pagerduty.com/'
FETCH_LIMIT = 100
TEAM_FETCH_LIMIT = 25

services_chunk_cache = {}


class InvalidServiceException(Exception):
    pass


class InvalidApiKeyException(Exception):
    pass


def fetch_incident_chunk(
    pd_api_key: str,
    service_ids: List[str],
    team_ids: List[str],
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
        'since': start_date,
        'until': end_date,
        'limit': str(limit),
        'offset': str(offset)
    }
    if service_ids:
        params['service_ids[]'] = service_ids

    if team_ids:
        params['team_ids[]'] = team_ids

    r = requests.get(PAGER_DUTY_API + 'incidents', headers=headers, params=params)

    if r.status_code == 400:
        raise InvalidServiceException('400 from PagerDuty. Make sure you have legit service_ids specified')
    if r.status_code == 404:
        raise InvalidApiKeyException('404 from PagerDuty. Double check your api key')

    return r.json()['incidents']


def fetch_all_incidents(
    pd_api_key: str,
    service_ids: List[str],
    team_ids: List[str],
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
            team_ids=team_ids,
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


def fetch_teams_chunk(
    pd_api_key: str,
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
        'limit': str(limit),
        'offset': str(offset)
    }
    r = requests.get(PAGER_DUTY_API + 'teams', headers=headers, params=params)

    return r.json()['teams']


def fetch_all_teams(
    pd_api_key: str
) -> List[Dict]:
    all_teams = []
    offset = 0
    while True:
        teams_chunk = fetch_teams_chunk(
            pd_api_key=pd_api_key,
            limit=TEAM_FETCH_LIMIT,
            offset=offset
        )
        if len(teams_chunk) == 0:
            break
        all_teams += teams_chunk
        offset += TEAM_FETCH_LIMIT

    return all_teams


def fetch_service_chunk(
    pd_api_key: str,
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
        'limit': str(limit),
        'offset': str(offset)
    }
    r = requests.get(PAGER_DUTY_API + 'services', headers=headers, params=params)

    return r.json()['services']


def fetch_all_services(
    pd_api_key: str
) -> List[Dict]:
    global services_chunk_cache
    if pd_api_key in services_chunk_cache:
        return services_chunk_cache[pd_api_key]
    all_services = []
    offset = 0
    while True:
        services_chunk = fetch_service_chunk(
            pd_api_key=pd_api_key,
            limit=TEAM_FETCH_LIMIT,
            offset=offset
        )
        if len(services_chunk) == 0:
            break
        all_services += services_chunk
        offset += TEAM_FETCH_LIMIT

    services_chunk_cache[pd_api_key] = all_services
    return all_services
