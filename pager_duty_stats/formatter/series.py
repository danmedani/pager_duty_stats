from typing import Dict
from typing import List
from typing import Set

from typing_extensions import TypedDict

from pager_duty_stats.logic.aggregation import AggregationType
from pager_duty_stats.logic.aggregation import AggregrateStats
from pager_duty_stats.logic.util.dates import step_through_dates


class SeriesRow(TypedDict):
    name: str
    data: List[int]


class SeriesResponse(TypedDict):
    xaxis: List[str]
    series: List[SeriesRow]


def get_aggregation_type_values(
    stats: Dict[str, AggregrateStats],
    aggregation_types: List[AggregationType]
) -> Dict[AggregationType, List[str]]:
    aggregation_type_values: Dict[AggregationType, Set[str]] = {
        aggregation_type: set()
        for aggregation_type in aggregation_types
    }

    for _, aggregation_stats in stats.items():
        for aggregation_type in aggregation_types:
            for name, _ in aggregation_stats['aggregations'][aggregation_type].items():
                aggregation_type_values[aggregation_type].add(name)

    # listify and sort the sets
    return {
        aggregation_type: sorted(list(aggregation_type_values[aggregation_type]))
        for aggregation_type in aggregation_types
    }


def get_xaxis(start_date: str, end_date: str, stats_map: Dict[str, AggregrateStats],) -> List[str]:
    xaxis = []
    for date in step_through_dates(start_date, end_date):
        if date in stats_map:
            xaxis.append(date)
    return xaxis


def extract_aggregation(
    aggregation_type: AggregationType,
    aggregation_values: List[str],
    stats_map: Dict[str, AggregrateStats],
    start_date: str,
    end_date: str
) -> List[SeriesRow]:
    aggregation = []
    for aggregation_value in aggregation_values:
        series_row = SeriesRow(
            name=aggregation_value,
            data=[]
        )
        for date in step_through_dates(start_date, end_date):
            if date in stats_map:
                series_row['data'].append(
                    stats_map[date]['aggregations'][aggregation_type][aggregation_value]
                )
        aggregation.append(series_row)
    return aggregation


def format_series_from_stats(
    aggregation_type: AggregationType,
    stats_map: Dict[str, AggregrateStats],
    start_date: str,
    end_date: str
) -> SeriesResponse:
    aggregation_values: Dict[AggregationType, List[str]] = get_aggregation_type_values(
        stats=stats_map,
        aggregation_types=[aggregation_type]
    )

    return SeriesResponse(
        xaxis=get_xaxis(start_date, end_date, stats_map),
        series=extract_aggregation(
            aggregation_type=aggregation_type,
            aggregation_values=aggregation_values[aggregation_type],
            stats_map=stats_map,
            start_date=start_date,
            end_date=end_date
        )
    )
