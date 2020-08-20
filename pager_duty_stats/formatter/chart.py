from datetime import datetime
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional


class ChartRequest(NamedTuple):
    service_ids: Optional[List[str]]
    team_ids: Optional[List[str]]
    start_date: str
    end_date: Optional[str]
    grouping_window: str
    chart_type: str


def parse_chart_request(request_json: Dict) -> ChartRequest:
    return ChartRequest(
        service_ids=request_json['service_ids'].split(',') if 'service_ids' in request_json else None,
        team_ids=request_json['team_ids'].split(',') if 'team_ids' in request_json else None,
        start_date=request_json['start_date'],
        end_date=request_json['end_date'] or str(datetime.now().date()),
        grouping_window=request_json['grouping_window'],
        chart_type=request_json['chart_type']
    )
