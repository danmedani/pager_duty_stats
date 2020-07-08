from typing import Optional
from typing import Dict
from datetime import datetime
from typing import List
from typing import NamedTuple
from flask import request
from flask import Flask
from pager_duty_stats.logic.aggregation import get_stats
from pager_duty_stats.logic.aggregation import AggregationType
from flask import jsonify
from pager_duty_stats.logic.pager_duty_client import fetch_all_incidents
from pager_duty_stats.logic.incident_types import ExtractionTechnique
from pager_duty_stats.logic.aggregation import GroupingWindow
from pager_duty_stats.formatter.series import format_series_from_stats

app = Flask(__name__, static_folder='../ui/dist/', static_url_path='')

class ChartRequest(NamedTuple):
    service_ids: List[str]
    start_date: str
    end_date: Optional[str]
    grouping_window: str

    pd_api_key: str

def parse_chart_request(request_json: Dict) -> ChartRequest:
    return ChartRequest(
        service_ids=request_json['service_ids'].split(','),
        start_date=request_json['start_date'],
        end_date=request_json['end_date'] or str(datetime.now().date()),
        grouping_window=request_json['grouping_window'],
        pd_api_key=request_json['pd_api_key']
    )


@app.route('/')
def index():
    return app.send_static_file('chart.html')


@app.route('/api/chart', methods=['POST'])
def chart():
    chart_request = parse_chart_request(request.json)
    incidents = fetch_all_incidents(
        pd_api_key=chart_request.pd_api_key, # todo: make this betterer
        service_ids=chart_request.service_ids,
        start_date=chart_request.start_date,
        end_date=chart_request.end_date
    )
    stats = get_stats(
        incidents=incidents,
        start_date=chart_request.start_date,
        end_date=chart_request.end_date,
        grouping_window=GroupingWindow.WEEK if chart_request.grouping_window == 'week' else GroupingWindow.DAY,
        incident_type_extraction_technique=ExtractionTechnique.YC,
        max_incident_types=10,
        aggregation_types=[AggregationType.SERVICE_NAME]
    )
    
    return jsonify(format_series_from_stats(stats))
