from typing_extensions import TypedDict
from typing import List
from typing import Dict
from pager_duty_stats.logic.aggregation import AggregrateStats

class SeriesRow(TypedDict):
    name: str
    data: List[int]

class SeriesResponse(TypedDict):
    xaxis: List[str]
    series: List[SeriesRow]

def format_series_from_stats(stats_map: Dict[str, AggregrateStats]) -> SeriesResponse:
    return SeriesResponse(
        xaxis=['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-04'],
        series=[
            SeriesRow(
                name='Yelp Connect Low Urgency',
                data=[1, 4, 7, 12]
            ),
            SeriesRow(
                name='Yelp Connect Critical Urgency',
                data=[0, 2, 1, 5]
            )
        ]
    )
