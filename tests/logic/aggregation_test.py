from collections import defaultdict
from datetime import datetime
from datetime import timezone

from pager_duty_stats.logic.aggregation import AggregationType
from pager_duty_stats.logic.aggregation import AggregrateStats
from pager_duty_stats.logic.aggregation import classify_incident_time
from pager_duty_stats.logic.aggregation import fill_out_empty_days
from pager_duty_stats.logic.aggregation import get_stats_by_day
from pager_duty_stats.logic.aggregation import IncidentTime
from pager_duty_stats.logic.aggregation import is_week_day

EMPTY_STATS = AggregrateStats(
    total_pages=0,
    aggregations={AggregationType.SERVICE_NAME: defaultdict(int), AggregationType.TIME_OF_DAY: defaultdict(int)}
)


def test_is_mon_week_day():
    assert is_week_day(datetime.strptime('2020-05-18', '%Y-%m-%d').replace(tzinfo=timezone.utc))


def test_is_sun_week_day():
    assert not is_week_day(datetime.strptime('2020-05-17', '%Y-%m-%d').replace(tzinfo=timezone.utc))


def test_is_sat_week_day():
    assert not is_week_day(datetime.strptime('2020-05-16', '%Y-%m-%d').replace(tzinfo=timezone.utc))


def test_fill_out_empty_days():
    jan_5_stats = AggregrateStats(
        total_pages=5,
        aggregations={
            AggregationType.SERVICE_NAME: {
                'service a': 2,
                'service b': 3,
            },
            AggregationType.TIME_OF_DAY: {
                str(IncidentTime.WORK): 4,
                str(IncidentTime.SLEEP): 1
            },
        }
    )
    jan_8_stats = AggregrateStats(
            total_pages=10,
            aggregations={
                AggregationType.SERVICE_NAME: {
                    'service a': 1,
                    'service b': 1,
                },
                AggregationType.TIME_OF_DAY: {
                    str(IncidentTime.WORK): 2
                },
            }
        )

    assert fill_out_empty_days(
        stats={
            '2020-01-05': jan_5_stats,
            '2020-01-08': jan_8_stats
        },
        start_date='2019-12-28',
        end_date='2020-01-10',
        aggregation_types=[AggregationType.SERVICE_NAME, AggregationType.TIME_OF_DAY]
    ) == {
        '2019-12-28': EMPTY_STATS,
        '2019-12-29': EMPTY_STATS,
        '2019-12-30': EMPTY_STATS,
        '2019-12-31': EMPTY_STATS,
        '2020-01-01': EMPTY_STATS,
        '2020-01-02': EMPTY_STATS,
        '2020-01-03': EMPTY_STATS,
        '2020-01-04': EMPTY_STATS,
        '2020-01-05': jan_5_stats,
        '2020-01-06': EMPTY_STATS,
        '2020-01-07': EMPTY_STATS,
        '2020-01-08': jan_8_stats,
        '2020-01-09': EMPTY_STATS,
        '2020-01-10': EMPTY_STATS,
    }


def test_classify_incident_time():
    assert classify_incident_time(datetime(2008, 12, 12, 4)) == IncidentTime.SLEEP
    assert classify_incident_time(datetime(2008, 12, 12, 7)) == IncidentTime.SLEEP
    assert classify_incident_time(datetime(2008, 12, 12, 8)) == IncidentTime.WORK
    assert classify_incident_time(datetime(2008, 12, 12, 14)) == IncidentTime.WORK
    assert classify_incident_time(datetime(2008, 12, 12, 18)) == IncidentTime.LEISURE
    assert classify_incident_time(datetime(2008, 12, 12, 19)) == IncidentTime.LEISURE
    assert classify_incident_time(datetime(2008, 12, 12, 20)) == IncidentTime.LEISURE


def test_get_stats_by_day_no_aggregation_types():
    assert get_stats_by_day(
        incidents=[
            {
                'created_at': '2020-05-18T16:00:50Z'
            },
            {
                'created_at': '2020-05-19T16:00:50Z'
            },
            {
                'created_at': '2020-05-19T17:00:50Z'
            },
            {
                'created_at': '2020-05-20T16:00:50Z'
            }
        ],
        start_date='2020-05-17',
        end_date='2020-05-20',
        aggregation_types=[],
        max_incident_types=None,
        incident_type_extraction_technique=None
    ) == {
        '2020-05-17': AggregrateStats(
            total_pages=0, aggregations={}
        ),
        '2020-05-18': AggregrateStats(
            total_pages=1, aggregations={}
        ),
        '2020-05-19': AggregrateStats(
            total_pages=2, aggregations={}
        ),
        '2020-05-20': AggregrateStats(
            total_pages=1, aggregations={}
        )
    }


def test_get_stats_by_day_with_per_service():
    assert get_stats_by_day(
        incidents=[
            {
                'created_at': '2020-05-18T16:00:50Z',
                'service': {'summary': 'service A'}
            },
            {
                'created_at': '2020-05-19T16:00:50Z',
                'service': {'summary': 'service A'}
            },
            {
                'created_at': '2020-05-19T18:00:50Z',
                'service': {'summary': 'service A'}
            },
            {
                'created_at': '2020-05-19T17:00:50Z',
                'service': {'summary': 'service B'}
            },
            {
                'created_at': '2020-05-20T16:00:50Z',
                'service': {'summary': 'service B'}
            }
        ],
        start_date='2020-05-17',
        end_date='2020-05-20',
        aggregation_types=[AggregationType.SERVICE_NAME],
        max_incident_types=None,
        incident_type_extraction_technique=None
    ) == {
        '2020-05-17': AggregrateStats(
            total_pages=0,
            aggregations={
                AggregationType.SERVICE_NAME: {}
            }
        ),
        '2020-05-18': AggregrateStats(
            total_pages=1,
            aggregations={
                AggregationType.SERVICE_NAME: {
                    'service A': 1
                }
            }
        ),
        '2020-05-19': AggregrateStats(
            total_pages=3,
            aggregations={
                AggregationType.SERVICE_NAME: {
                    'service A': 2,
                    'service B': 1
                }
            }
        ),
        '2020-05-20': AggregrateStats(
            total_pages=1,
            aggregations={
                AggregationType.SERVICE_NAME: {
                    'service B': 1
                }
            }
        )
    }
