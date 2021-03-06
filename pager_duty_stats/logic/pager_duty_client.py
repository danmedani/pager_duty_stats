from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List

import requests

from pager_duty_stats.logic.util.dates import step_through_date_range_chunks

"""
Useful reference: https://developer.pagerduty.com/api-reference/
"""

PAGER_DUTY_API = 'https://api.pagerduty.com/'
FETCH_LIMIT = 100
TEAM_FETCH_LIMIT = 25

services_chunk_cache: Dict[str, List[Dict]] = {}
teams_chunk_cache: Dict[str, List[Dict]] = {}


class InvalidServiceException(Exception):
    pass


class InvalidApiKeyException(Exception):
    pass


def get_headers(bearer_token: str):
    return {
        'Authorization': 'Bearer ' + bearer_token,
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Content-Type': 'application/json',
    }


def fetch_abilities(
    bearer_token: str,
) -> List[str]:
    r = requests.get(PAGER_DUTY_API + 'abilities', headers=get_headers(bearer_token))
    if r.status_code != 200:
        raise InvalidApiKeyException('404 from PagerDuty. Double check your api key')

    return r.json()['abilities']


def fetch_incident_chunk(
    bearer_token: str,
    service_ids: List[str],
    team_ids: List[str],
    start_date: str,
    end_date: str,
    limit: int,
    offset: int
) -> List[Dict]:
    params = {
        'since': start_date,
        'until': end_date,
        'limit': str(limit),
        'offset': str(offset)
    }
    if service_ids:
        params['service_ids[]'] = service_ids  # type: ignore

    if team_ids:
        params['team_ids[]'] = team_ids  # type: ignore

    r = requests.get(PAGER_DUTY_API + 'incidents', headers=get_headers(bearer_token), params=params)

    if r.status_code == 400:
        raise InvalidServiceException('400 from PagerDuty. Make sure you have legit service_ids specified')
    if r.status_code == 404:
        raise InvalidApiKeyException('404 from PagerDuty. Double check your api key')

    return r.json()['incidents']


def fetch_all_incidents(
    bearer_token: str,
    service_ids: List[str],
    team_ids: List[str],
    start_date: str,
    end_date: str
) -> List[Dict]:
    all_incidents = []

    # pagerduty api defaults to exclusive end-date (it uses 00:00 of the date). add a day to compensate
    end_date_plus_one = str((datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).date())

    for start, end in step_through_date_range_chunks(start_date, end_date_plus_one):
        offset = 0
        while True:
            incidents = fetch_incident_chunk(
                bearer_token=bearer_token,
                service_ids=service_ids,
                team_ids=team_ids,
                start_date=start,
                end_date=end,
                limit=FETCH_LIMIT,
                offset=offset
            )
            if len(incidents) == 0:
                break
            all_incidents += incidents
            offset += FETCH_LIMIT

    return all_incidents


def fetch_teams_chunk(
    bearer_token: str,
    limit: int,
    offset: int
) -> List[Dict]:
    params = {
        'limit': str(limit),
        'offset': str(offset)
    }
    r = requests.get(PAGER_DUTY_API + 'teams', headers=get_headers(bearer_token), params=params)

    return r.json()['teams']


def fetch_all_teams(
    bearer_token: str,
) -> List[Dict]:
    global teams_chunk_cache
    # if pd_api_key in teams_chunk_cache:
    #     return teams_chunk_cache[pd_api_key]

    all_teams = []
    offset = 0
    while True:
        teams_chunk = fetch_teams_chunk(
            bearer_token=bearer_token,
            limit=TEAM_FETCH_LIMIT,
            offset=offset
        )
        if len(teams_chunk) == 0:
            break
        all_teams += teams_chunk
        offset += TEAM_FETCH_LIMIT

    teams_chunk_cache[bearer_token] = all_teams
    return all_teams


def fetch_service_chunk(
    bearer_token: str,
    limit: int,
    offset: int
) -> List[Dict]:
    params = {
        'limit': str(limit),
        'offset': str(offset)
    }
    r = requests.get(PAGER_DUTY_API + 'services', headers=get_headers(bearer_token), params=params)

    return r.json()['services']


def fetch_all_services(
    bearer_token: str,
) -> List[Dict]:
    global services_chunk_cache
    # if pd_api_key in services_chunk_cache:
    #     return services_chunk_cache[pd_api_key]
    all_services = []
    offset = 0
    while True:
        services_chunk = fetch_service_chunk(
            bearer_token=bearer_token,
            limit=TEAM_FETCH_LIMIT,
            offset=offset
        )
        if len(services_chunk) == 0:
            break
        all_services += services_chunk
        offset += TEAM_FETCH_LIMIT

    services_chunk_cache[bearer_token] = all_services
    return all_services
