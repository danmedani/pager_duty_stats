from typing import Optional
from typing import Dict
from datetime import datetime
from typing import List
from typing import NamedTuple
from flask import request
from flask import Flask
from flask import jsonify
from pager_duty_stats.logic.pager_duty_client import fetch_all_incidents

app = Flask(__name__, static_folder='../ui/dist/', static_url_path='')

class ChartRequest(NamedTuple):
    service_ids: List[str]
    start_date: str
    end_date: Optional[str]
    grouping_window: str


def parse_chart_request(request_json: Dict) -> ChartRequest:
    return ChartRequest(
        service_ids=request_json['service_ids'].split(','),
        start_date=request_json['start_date'],
        end_date=request_json['end_date'] or str(datetime.now().date()),
        grouping_window=request_json['grouping_window']
    )


@app.route('/')
def index():
    return app.send_static_file('chart.html')

@app.route('/api/chart', methods=['POST'])
def chart():
    chart_request = parse_chart_request(request.json)
    all_incidents = fetch_all_incidents(
        pd_api_key='***',
        service_ids=chart_request.service_ids,
        start_date=chart_request.start_date,
        end_date=chart_request.end_date
    )
    print(all_incidents)
    return jsonify({
        'phar': 123
    })
