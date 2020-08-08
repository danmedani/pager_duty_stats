from datetime import datetime
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
import urllib
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import request
import pkce
import os
from pager_duty_stats.formatter.series import format_series_from_stats
from pager_duty_stats.logic.aggregation import AggregationType
from pager_duty_stats.logic.aggregation import get_stats
from pager_duty_stats.logic.aggregation import GroupingWindow
from pager_duty_stats.logic.incident_types import ExtractionTechnique
from pager_duty_stats.logic.pager_duty_client import fetch_abilities
from pager_duty_stats.logic.pager_duty_client import fetch_all_incidents
from pager_duty_stats.logic.pager_duty_client import fetch_all_services
from pager_duty_stats.logic.pager_duty_client import fetch_all_teams
import requests

from os import environ, path
from dotenv import load_dotenv

application = Flask(__name__, static_folder='../ui/dist/', static_url_path='')
global_code_verifier = ''
global_access_token = ''



if application.config['ENV'] == 'development':
    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, '.env'))


class ChartRequest(NamedTuple):
    service_ids: Optional[List[str]]
    team_ids: Optional[List[str]]
    start_date: str
    end_date: Optional[str]
    grouping_window: str
    chart_type: str
    pd_api_key: str


def parse_chart_request(request_json: Dict) -> ChartRequest:
    return ChartRequest(
        service_ids=request_json['service_ids'].split(',') if 'service_ids' in request_json else None,
        team_ids=request_json['team_ids'].split(',') if 'team_ids' in request_json else None,
        start_date=request_json['start_date'],
        end_date=request_json['end_date'] or str(datetime.now().date()),
        grouping_window=request_json['grouping_window'],
        chart_type=request_json['chart_type'],
        pd_api_key=request_json['pd_api_key']
    )


def get_pager_duty_client_id():
    return os.environ['PAGERDUTY_OAUTH_CLIENT_ID']


@application.route('/')
def index():
    return application.send_static_file('index.html')


@application.route('/stats')
def stats():
    return application.send_static_file('stats.html')


# @application.route('/oauth_landing')
# def oauth_landing():
#     return application.send_static_file('oauth_landing.html')


# @application.route('/api/pager_duty_oauth_landing')
# def pager_duty_oauth_landing():
#     if 'error' in request.args:
#         print('error!', request.args.get('error_description'))
#         return application.send_static_file('index.html')
#     else:
#         code = request.args.get('code')
#         # subdomain = request.args.get('subdomain')

#         headers = {
#             'Content-Type': 'application/json',
#             'Accept': 'application/json'
#         }
#         params = {
#             'grant_type': 'authorization_code',
#             'client_id': get_pager_duty_client_id(),
#             'redirect_uri': get_oauth_rediection_uri(),
#             'code': code,
#             'code_verifier': global_code_verifier
#         }
#         r = requests.post('https://app.pagerduty.com/oauth/token', headers=headers, params=params)

#         global_access_token = r.json()['access_token']

#     return application.send_static_file('index.html')


@application.route('/api/auth')
def auth():
    fetch_abilities(pd_api_key=request.args.get('pd_api_key'))
    return jsonify(
        {
            'auth_status': 'OK'
        }
    )


@application.before_request
def reroute_http_to_https():
    if not request.is_secure and not application.config['ENV'] == 'development':
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


@application.route('/api/chart', methods=['POST'])
def chart():
    chart_request = parse_chart_request(request.json)
    incidents = fetch_all_incidents(
        pd_api_key=chart_request.pd_api_key,  # todo: make this betterer
        service_ids=chart_request.service_ids,
        team_ids=chart_request.team_ids,
        start_date=chart_request.start_date,
        end_date=chart_request.end_date
    )
    stats = get_stats(
        incidents=incidents,
        start_date=chart_request.start_date,
        end_date=chart_request.end_date,
        grouping_window=GroupingWindow.WEEK if chart_request.grouping_window == 'week' else GroupingWindow.DAY,
        incident_type_extraction_technique=ExtractionTechnique.YC,
        max_incident_types=25,
        aggregation_types=[
            AggregationType.SERVICE_NAME,
            AggregationType.TIME_OF_DAY,
            AggregationType.CUSTOM_INCIDENT_TYPE
        ]
    )

    return jsonify(
        format_series_from_stats(
            start_date=chart_request.start_date,
            end_date=chart_request.end_date,
            stats_map=stats,
            aggregation_type=AggregationType[chart_request.chart_type]
        )
    )


@application.route('/api/teams', methods=['GET'])
def teams():
    return jsonify(
        [
            {
                'id': team['id'],
                'name': team['name'],
            }
            for team in fetch_all_teams(pd_api_key=request.args.get('pd_api_key'))
        ]
    )


@application.route('/api/services', methods=['GET'])
def services():
    return jsonify(
        [
            {
                'id': team['id'],
                'name': team['name'],
            }
            for team in fetch_all_services(pd_api_key=request.args.get('pd_api_key'))
        ]
    )


if __name__ == "__main__":
    application.debug = True
    application.run()
