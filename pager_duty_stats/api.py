from flask import Blueprint
from flask import jsonify
from flask import request

from pager_duty_stats.formatter.chart import parse_chart_request
from pager_duty_stats.formatter.series import format_series_from_stats
from pager_duty_stats.logic.aggregation import AggregationType
from pager_duty_stats.logic.aggregation import get_stats
from pager_duty_stats.logic.aggregation import GroupingWindow
from pager_duty_stats.logic.incident_types import ExtractionTechnique
from pager_duty_stats.logic.pager_duty_client import fetch_abilities
from pager_duty_stats.logic.pager_duty_client import fetch_all_incidents
from pager_duty_stats.logic.pager_duty_client import fetch_all_services
from pager_duty_stats.logic.pager_duty_client import fetch_all_teams

api = Blueprint('api', __name__)


@api.route('/api/auth')
def auth():
    # This throws an exception if the token isn't OK
    fetch_abilities(bearer_token=request.headers.get('Authorization'))

    return {}


@api.route('/api/teams', methods=['GET'])
def teams():
    return jsonify(
        [
            {
                'id': team['id'],
                'name': team['name'],
            }
            for team in fetch_all_teams(bearer_token=request.headers.get('Authorization'))
        ]
    )


@api.route('/api/services', methods=['GET'])
def services():
    return jsonify(
        [
            {
                'id': team['id'],
                'name': team['name'],
            }
            for team in fetch_all_services(bearer_token=request.headers.get('Authorization'))
        ]
    )


@api.route('/api/chart', methods=['POST'])
def chart():
    chart_request = parse_chart_request(request.json)
    incidents = fetch_all_incidents(
        bearer_token=request.headers.get('Authorization'),
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
