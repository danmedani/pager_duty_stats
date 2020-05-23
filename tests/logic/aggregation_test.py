from collections import defaultdict
from datetime import datetime
from datetime import timezone

import mock

from pager_duty_stats.logic.aggregation import AggregationType
from pager_duty_stats.logic.aggregation import AggregrateStats
from pager_duty_stats.logic.aggregation import classify_incident_time
from pager_duty_stats.logic.aggregation import clean_error_type_counts
from pager_duty_stats.logic.aggregation import convert_day_stats_to_week_stats
from pager_duty_stats.logic.aggregation import extract_aggregation_value
from pager_duty_stats.logic.aggregation import ExtractionTechnique
from pager_duty_stats.logic.aggregation import fill_out_empty_days
from pager_duty_stats.logic.aggregation import find_next_monday
from pager_duty_stats.logic.aggregation import get_earliest_date
from pager_duty_stats.logic.aggregation import get_stats
from pager_duty_stats.logic.aggregation import get_stats_by_day
from pager_duty_stats.logic.aggregation import get_weekday_index
from pager_duty_stats.logic.aggregation import GroupingWindow
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


def test_get_earliest_date():
    assert get_earliest_date(['2020-02-02', '2019-03-01']) == '2019-03-01'
    assert get_earliest_date(['2020-02-02', '2020-02-01']) == '2020-02-01'
    assert get_earliest_date(['2020-02-02']) == '2020-02-02'
    assert get_earliest_date(['2020-02-02', '2019-03-01', '2019-02-01']) == '2019-02-01'
    assert get_earliest_date(['2020-08-22', '2020-02-02', '2019-03-01', '2019-11-11']) == '2019-03-01'
    assert get_earliest_date(['2017-02-02', '2019-03-01']) == '2017-02-02'


def test_find_next_monday():
    assert find_next_monday('2020-05-22') == '2020-05-25'
    assert find_next_monday('2020-05-23') == '2020-05-25'
    assert find_next_monday('2020-05-24') == '2020-05-25'
    assert find_next_monday('2020-05-25') == '2020-05-25'


def test_get_weekday_index():
    assert get_weekday_index('2020-05-22') == 4
    assert get_weekday_index('2020-05-21') == 3
    assert get_weekday_index('2020-05-23') == 5
    assert get_weekday_index('2020-05-24') == 6


def test_classify_incident_time():
    assert classify_incident_time(datetime(2008, 12, 12, 4)) == IncidentTime.SLEEP
    assert classify_incident_time(datetime(2008, 12, 12, 7)) == IncidentTime.SLEEP
    assert classify_incident_time(datetime(2008, 12, 12, 8)) == IncidentTime.WORK
    assert classify_incident_time(datetime(2008, 12, 12, 14)) == IncidentTime.WORK
    assert classify_incident_time(datetime(2008, 12, 12, 18)) == IncidentTime.LEISURE
    assert classify_incident_time(datetime(2008, 12, 12, 19)) == IncidentTime.LEISURE
    assert classify_incident_time(datetime(2008, 12, 12, 20)) == IncidentTime.LEISURE
    assert classify_incident_time(datetime(2020, 5, 23, 12)) == IncidentTime.LEISURE
    assert classify_incident_time(datetime(2020, 5, 23, 9)) == IncidentTime.LEISURE


def create_incidents(summary: str, created_at: str, title: str):
    incidents = {}
    incidents['service'] = {}
    incidents['service']['summary'] = summary
    incidents['created_at'] = created_at
    incidents['title'] = title

    return incidents


def test_extract_aggregation_value_for_service_name():
    incidents = create_incidents('test_service_summary', '2020-05-23T05:51:58Z', 'test_title')

    assert extract_aggregation_value(
        incidents,
        AggregationType.SERVICE_NAME,
        ExtractionTechnique.TITLE
    ) == 'test_service_summary'


def test_extract_aggregation_value_for_custom_incident_type():
    incidents = create_incidents('test_service_summary', '2020-05-23T05:51:58Z', 'test_title')

    assert extract_aggregation_value(
        incidents,
        AggregationType.CUSTOM_INCIDENT_TYPE,
        ExtractionTechnique.TITLE
    ) == 'test_title'

    assert extract_aggregation_value(
        incidents,
        AggregationType.CUSTOM_INCIDENT_TYPE,
        ExtractionTechnique.YC
    ) == 'test_title'

    incidents2 = create_incidents('test_service_summary', '2020-05-23T05:51:58Z', 'Title: Test')

    assert extract_aggregation_value(
        incidents2,
        AggregationType.CUSTOM_INCIDENT_TYPE,
        ExtractionTechnique.YC
    ) == 'Title: Test'


@mock.patch('pager_duty_stats.logic.aggregation.classify_incident_time')
def test_extract_aggregation_value_for_time_of_day(
    mock_classify_incident_time
):
    mock_classify_incident_time.return_value = IncidentTime.LEISURE
    assert extract_aggregation_value(
        create_incidents('test_service_summary', '2020-05-23T03:51:58Z', 'test_title'),
        AggregationType.TIME_OF_DAY,
        ExtractionTechnique.YC
    ) == 'leisure'


def test_extract_aggregation_value_for_unsupported_aggregation_type():
    incidents = create_incidents('test_service_summary', '2020-05-23T05:51:58Z', 'test_title')

    assert extract_aggregation_value(
        incidents,
        AggregationType.SERVICE_NAME,
        ExtractionTechnique.TITLE
    ) == 'test_service_summary'


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


def test_get_stats_by_day_with_custom():
    assert get_stats_by_day(
        incidents=[
            {
                'created_at': '2020-05-18T16:00:50Z',
                'title': 'Page A'
            },
            {
                'created_at': '2020-05-18T15:00:50Z',
                'title': 'Page A'
            },
            {
                'created_at': '2020-05-18T16:00:50Z',
                'title': 'Page B'
            },
            {
                'created_at': '2020-05-18T16:00:50Z',
                'title': 'Page C'
            },
            {
                'created_at': '2020-05-19T16:00:50Z',
                'title': 'Page B'
            }
        ],
        start_date='2020-05-18',
        end_date='2020-05-19',
        aggregation_types=[AggregationType.CUSTOM_INCIDENT_TYPE],
        max_incident_types=2,
        incident_type_extraction_technique=ExtractionTechnique.TITLE
    ) == {
        '2020-05-18': AggregrateStats(
            total_pages=4,
            aggregations={
                AggregationType.CUSTOM_INCIDENT_TYPE: {
                    'Page A': 2,
                    'Page B': 1,
                    'miscellaneous': 1,
                }
            }
        ),
        '2020-05-19': AggregrateStats(
            total_pages=1,
            aggregations={
                AggregationType.CUSTOM_INCIDENT_TYPE: {
                    'Page B': 1
                }
            }
        ),
    }


def test_clean_error_type_counts():
    # page A, C, & E have more
    assert clean_error_type_counts(
        stats={
            '2020-01-01': AggregrateStats(
                total_pages=9,
                aggregations={
                    AggregationType.CUSTOM_INCIDENT_TYPE: {
                        'Page A': 1,
                        'Page B': 1,
                        'Page C': 5,
                        'Page D': 1,
                        'Page E': 1,
                    }
                }
            ),
            '2020-01-02': AggregrateStats(
                total_pages=5,
                aggregations={
                    AggregationType.CUSTOM_INCIDENT_TYPE: {
                        'Page A': 1,
                        'Page B': 1,
                        'Page C': 1,
                        'Page D': 1,
                        'Page E': 1,
                    }
                }
            ),
            '2020-01-03': AggregrateStats(
                total_pages=8,
                aggregations={
                    AggregationType.CUSTOM_INCIDENT_TYPE: {
                        'Page A': 2,
                        'Page B': 1,
                        'Page C': 1,
                        'Page D': 1,
                        'Page E': 3,
                    }
                }
            )
        },
        max_incident_types=3
    ) == {
        '2020-01-01': AggregrateStats(
            total_pages=9,
            aggregations={
                AggregationType.CUSTOM_INCIDENT_TYPE: {
                    'Page A': 1,
                    'Page C': 5,
                    'Page E': 1,
                    'miscellaneous': 2
                }
            }
        ),
        '2020-01-02': AggregrateStats(
            total_pages=5,
            aggregations={
                AggregationType.CUSTOM_INCIDENT_TYPE: {
                    'Page A': 1,
                    'Page C': 1,
                    'Page E': 1,
                    'miscellaneous': 2
                }
            }
        ),
        '2020-01-03': AggregrateStats(
            total_pages=8,
            aggregations={
                AggregationType.CUSTOM_INCIDENT_TYPE: {
                    'Page A': 2,
                    'Page C': 1,
                    'Page E': 3,
                    'miscellaneous': 2
                }
            }
        )
    }


def test_clean_error_type_counts_no_cleaning_necessary():
    mock_stats = {
        '2020-01-01': AggregrateStats(
            total_pages=9,
            aggregations={
                AggregationType.CUSTOM_INCIDENT_TYPE: {
                    'Page A': 1,
                    'Page B': 1,
                    'Page C': 5,
                    'Page D': 1,
                    'Page E': 1,
                }
            }
        ),
        '2020-01-02': AggregrateStats(
            total_pages=5,
            aggregations={
                AggregationType.CUSTOM_INCIDENT_TYPE: {
                    'Page A': 1,
                    'Page B': 1,
                    'Page C': 1,
                    'Page D': 1,
                    'Page E': 1,
                }
            }
        ),
        '2020-01-03': AggregrateStats(
            total_pages=8,
            aggregations={
                AggregationType.CUSTOM_INCIDENT_TYPE: {
                    'Page A': 2,
                    'Page B': 1,
                    'Page C': 1,
                    'Page D': 1,
                    'Page E': 3,
                }
            }
        )
    }

    assert clean_error_type_counts(
        stats=mock_stats,
        max_incident_types=10
    ) == mock_stats


@mock.patch('pager_duty_stats.logic.aggregation.get_stats_by_day')
@mock.patch('pager_duty_stats.logic.aggregation.convert_day_stats_to_week_stats')
def test_get_stats_via_day(
    mock_convert_day_stats_to_week_stats,
    mock_get_stats_by_day
):
    stats_mock = mock.Mock()
    mock_get_stats_by_day.return_value = stats_mock
    assert get_stats(
        incidents=mock.Mock(),
        start_date='2020-01-01',
        end_date='2020-02-01',
        grouping_window=GroupingWindow.DAY,
        aggregation_types=[],
        incident_type_extraction_technique=mock.Mock(),
        max_incident_types=0
    ) == stats_mock
    mock_convert_day_stats_to_week_stats.assert_not_called()


@mock.patch('pager_duty_stats.logic.aggregation.get_stats_by_day')
@mock.patch('pager_duty_stats.logic.aggregation.convert_day_stats_to_week_stats')
def test_get_stats_via_week(
    mock_convert_day_stats_to_week_stats,
    mock_get_stats_by_day
):
    stats_mock = mock.Mock()
    week_mock = mock.Mock()
    mock_get_stats_by_day.return_value = stats_mock
    mock_convert_day_stats_to_week_stats.return_value = week_mock

    assert get_stats(
        incidents=mock.Mock(),
        start_date='2020-01-01',
        end_date='2020-02-01',
        grouping_window=GroupingWindow.WEEK,
        aggregation_types=[],
        incident_type_extraction_technique=mock.Mock(),
        max_incident_types=0
    ) == week_mock


def test_convert_day_stats_to_week_stats_one_week():
    # Grab 1 weeks worth
    a_stats = AggregrateStats(
        total_pages=9,
        aggregations={
            AggregationType.CUSTOM_INCIDENT_TYPE: {
                'Page A': 1,
                'Page B': 1,
                'Page C': 5,
                'Page D': 1,
                'Page E': 1,
            }
        }
    )
    convert_day_stats_to_week_stats(
        stats={
            '2020-05-01': a_stats,
            '2020-05-02': a_stats,
            '2020-05-03': a_stats,
            '2020-05-04': a_stats,  # mon
            '2020-05-05': a_stats,  # tus
            '2020-05-06': a_stats,  # wed
            '2020-05-07': a_stats,  # thu
            '2020-05-08': a_stats,  # fri
            '2020-05-09': a_stats,  # sat
            '2020-05-10': a_stats,  # sun
            '2020-05-11': a_stats,
        },
        end_date='2020-05-11',
        aggregation_types=[AggregationType.CUSTOM_INCIDENT_TYPE]
    ) == AggregrateStats(
        total_pages=45,
        aggregations={
            AggregationType.CUSTOM_INCIDENT_TYPE: {
                'Page A': 7,
                'Page B': 7,
                'Page C': 35,
                'Page D': 7,
                'Page E': 7,
            }
        }
    )
