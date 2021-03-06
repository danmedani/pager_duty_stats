import copy
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from enum import Enum
from typing import DefaultDict
from typing import Dict
from typing import List

from typing_extensions import TypedDict

from pager_duty_stats.logic.incident_types import extract_incident_type
from pager_duty_stats.logic.incident_types import ExtractionTechnique
from pager_duty_stats.logic.util.dates import step_through_dates

MISCELLANEOUS = 'miscellaneous'


class GroupingWindow(Enum):
    DAY = 'day'
    WEEK = 'week'


class AggregationType(Enum):
    SERVICE_NAME = 'service_name'
    TIME_OF_DAY = 'time_of_day'
    CUSTOM_INCIDENT_TYPE = 'custom_incident_type'


class AggregrateStats(TypedDict):
    total_pages: int
    aggregations: Dict[AggregationType, DefaultDict[str, int]]


class IncidentTime(Enum):
    WORK = 'work'
    SLEEP = 'sleep'
    LEISURE = 'leisure'

    # useful for making output human readable
    def __str__(self):
        return self.value


def get_local_datetime(iso_date: str):
    return datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).astimezone(tz=None)


def get_fresh_aggregate_stats(aggregation_types: List[AggregationType]) -> AggregrateStats:
    return AggregrateStats(
        total_pages=0,
        aggregations={
            aggregation_type: defaultdict(int)
            for aggregation_type in aggregation_types
        }
    )


def is_week_day(time: datetime) -> bool:
    return time.weekday() < 5


def classify_incident_time(time: datetime) -> IncidentTime:
    if time.hour < 8:
        return IncidentTime.SLEEP

    if not is_week_day(time):
        return IncidentTime.LEISURE

    return IncidentTime.WORK if time.hour < 18 else IncidentTime.LEISURE


def extract_aggregation_value(
    incident: Dict,
    aggregation_type: AggregationType,
    incident_type_extraction_technique: ExtractionTechnique
) -> str:
    if aggregation_type == AggregationType.SERVICE_NAME:
        return incident['service']['summary']

    if aggregation_type == AggregationType.TIME_OF_DAY:
        return str(
            classify_incident_time(
                get_local_datetime(
                    incident['created_at']
                )
            )
        )

    if aggregation_type == AggregationType.CUSTOM_INCIDENT_TYPE:
        return extract_incident_type(
            incident,
            incident_type_extraction_technique
        )

    raise Exception('Aggregation group {} not supported!'.format(aggregation_type))  # pragma nocover


def get_stats_by_day(
    incidents: List[Dict],
    start_date: str,
    end_date: str,
    aggregation_types: List[AggregationType],
    max_incident_types: int,
    incident_type_extraction_technique: ExtractionTechnique
) -> Dict[str, AggregrateStats]:
    incidents_by_day: Dict[str, AggregrateStats] = {}

    for incident in incidents:
        create_date_time = get_local_datetime(incident['created_at'])
        create_date = str(create_date_time.date())
        if create_date not in incidents_by_day:
            incidents_by_day[create_date] = get_fresh_aggregate_stats(aggregation_types)

        incidents_by_day[create_date]['total_pages'] += 1

        for aggregation_type in aggregation_types:
            incidents_by_day[create_date]['aggregations'][aggregation_type][
                extract_aggregation_value(
                    incident,
                    aggregation_type,
                    incident_type_extraction_technique
                )
            ] += 1

    filled_out_stats = fill_out_empty_days(
        incidents_by_day,
        start_date,
        end_date,
        aggregation_types
    )

    if AggregationType.CUSTOM_INCIDENT_TYPE in aggregation_types:
        return clean_error_type_counts(
            filled_out_stats,
            max_incident_types
        )
    return filled_out_stats


def get_stats(
    incidents: List[Dict],
    start_date: str,
    end_date: str,
    grouping_window: GroupingWindow,
    aggregation_types: List[AggregationType],
    incident_type_extraction_technique: ExtractionTechnique,
    max_incident_types: int
):
    stats_by_day = get_stats_by_day(
        incidents,
        start_date,
        end_date,
        aggregation_types,
        max_incident_types,
        incident_type_extraction_technique
    )

    if grouping_window == GroupingWindow.DAY:
        return stats_by_day

    if grouping_window == GroupingWindow.WEEK:
        return convert_day_stats_to_week_stats(
            stats_by_day,
            end_date,
            aggregation_types
        )

    raise Exception('Grouping Window {} not recognized'.format(grouping_window))   # pragma: no cover


def fill_out_empty_days(
    stats: Dict[str, AggregrateStats],
    start_date: str,
    end_date: str,
    aggregation_types: List[AggregationType]
) -> Dict[str, AggregrateStats]:
    for date in step_through_dates(start_date, end_date):
        if date not in stats:
            stats[date] = get_fresh_aggregate_stats(aggregation_types)

    return stats


def get_earliest_date(dates: List[str]) -> str:
    earliest_date = str(datetime.now().date())
    for date in dates:
        if date < earliest_date:
            earliest_date = date
    return earliest_date


def find_next_monday(date: str) -> str:
    first_monday = datetime.strptime(date, '%Y-%m-%d')
    while first_monday.weekday() > 0:
        first_monday += timedelta(days=1)
    return str(first_monday.date())


def get_weekday_index(date: str) -> int:
    return datetime.strptime(date, '%Y-%m-%d').weekday()


def convert_day_stats_to_week_stats(
    stats: Dict[str, AggregrateStats],
    end_date: str,
    aggregation_types: List[AggregationType]
) -> Dict[str, AggregrateStats]:
    week_stats: Dict[str, AggregrateStats] = {}
    running_week_stats = get_fresh_aggregate_stats(aggregation_types)
    start_of_week = None

    start_date = find_next_monday(
        get_earliest_date(list(stats.keys()))
    )
    for date in step_through_dates(
        start_date,
        end_date
    ):
        if get_weekday_index(date) == 0:
            if start_of_week:
                week_stats[start_of_week] = running_week_stats

            running_week_stats = get_fresh_aggregate_stats(aggregation_types)
            start_of_week = date

        if date in stats:
            running_week_stats['total_pages'] += stats[date]['total_pages']

            for aggregation_type in aggregation_types:
                for name, count in stats[date]['aggregations'][aggregation_type].items():
                    running_week_stats['aggregations'][aggregation_type][name] += count

    if running_week_stats['total_pages'] > 0 and start_of_week:
        # We don't have a full week... include it anyways
        week_stats[start_of_week] = running_week_stats

    return week_stats


def clean_error_type_counts(
    stats: Dict[str, AggregrateStats],
    max_incident_types: int
) -> Dict[str, AggregrateStats]:
    # removes any errors that don't happen v often
    total_error_type_counts = {}
    for _, day_stats in stats.items():
        for error_type, error_type_count in day_stats['aggregations'][AggregationType.CUSTOM_INCIDENT_TYPE].items():
            if error_type not in total_error_type_counts:
                total_error_type_counts[error_type] = 0
            total_error_type_counts[error_type] += error_type_count

    total_error_type_counts_list = [(key, val) for key, val in total_error_type_counts.items()]
    total_error_type_counts_list_s = sorted(total_error_type_counts_list, key=lambda pair: -1 * pair[1])
    if len(total_error_type_counts_list_s) <= max_incident_types:
        # no need to hide anything
        return stats

    stats_to_keep = set(
        [incident_types for incident_types, _ in total_error_type_counts_list_s[:max_incident_types]]
    )

    new_stats = {}
    for day, _ in stats.items():
        new_stats[day] = copy.deepcopy(stats[day])
        for error_type, _ in stats[day]['aggregations'][AggregationType.CUSTOM_INCIDENT_TYPE].items():
            if error_type not in stats_to_keep:
                if MISCELLANEOUS not in new_stats[day]['aggregations'][AggregationType.CUSTOM_INCIDENT_TYPE]:
                    new_stats[day]['aggregations'][AggregationType.CUSTOM_INCIDENT_TYPE][MISCELLANEOUS] = 0

                new_stats[day]['aggregations'][
                    AggregationType.CUSTOM_INCIDENT_TYPE
                ][MISCELLANEOUS] += stats[day]['aggregations'][AggregationType.CUSTOM_INCIDENT_TYPE][error_type]

                del new_stats[day]['aggregations'][AggregationType.CUSTOM_INCIDENT_TYPE][error_type]

    return new_stats
