from datetime import datetime

import mock
import pytest

from pager_duty_stats.main import AggregationType
from pager_duty_stats.main import ExtractionTechnique
from pager_duty_stats.main import fetch_aggregation_types
from pager_duty_stats.main import GroupingWindow
from pager_duty_stats.main import InvalidOptionsException
from pager_duty_stats.main import Namespace
from pager_duty_stats.main import parse_args
from pager_duty_stats.main import run


def test_parse_args_defaults():
    assert parse_args([
        '--service-ids', 'service A', 'service B',
        '--start-date', '2020-01-01'
    ]) == Namespace(
        service_ids=['service A', 'service B'],
        start_date='2020-01-01',
        end_date=str(datetime.now().date()),
        grouping_window=GroupingWindow.WEEK,
        pd_key_file='.api_key',
        include_time_of_day_counts=False,
        include_incident_types=False,
        incident_type_extraction_technique=ExtractionTechnique.YC,
        max_incident_types=None
    )


def test_parse_args_no_start_date():
    with pytest.raises(SystemExit):
        parse_args([
            '--service-ids', 'service A', 'service B'
        ]) == Namespace(
            service_ids=['service A', 'service B'],
            start_date='2020-01-01',
            end_date=str(datetime.now().date()),
            grouping_window=GroupingWindow.WEEK,
            pd_key_file='.api_key',
            include_time_of_day_counts=False,
            include_incident_types=False,
            incident_type_extraction_technique=ExtractionTechnique.YC,
            max_incident_types=None
        )


def test_parse_args_no_services():
    with pytest.raises(SystemExit):
        parse_args([
            '--start-date', '2020-01-01'
        ]) == Namespace(
            start_date='2020-01-01',
            end_date=str(datetime.now().date()),
            grouping_window=GroupingWindow.WEEK,
            pd_key_file='.api_key',
            include_time_of_day_counts=False,
            include_incident_types=False,
            incident_type_extraction_technique=ExtractionTechnique.YC,
            max_incident_types=None
        )


def test_fetch_aggregation_types_no_max_incident_type_specified():
    with pytest.raises(InvalidOptionsException):
        fetch_aggregation_types(
            Namespace(
                service_ids=['service A', 'service B'],
                start_date='2020-01-01',
                include_time_of_day_counts=False,
                include_incident_types=True,
                max_incident_types=None
            )
        )


def test_fetch_aggregation_types_just_defaults():
    assert fetch_aggregation_types(Namespace(
        include_time_of_day_counts=False,
        include_incident_types=False
    )) == [AggregationType.SERVICE_NAME]


def test_fetch_aggregation_types_all_options():
    assert fetch_aggregation_types(Namespace(
        include_time_of_day_counts=True,
        include_incident_types=True,
        max_incident_types=4
    )) == [AggregationType.SERVICE_NAME, AggregationType.TIME_OF_DAY, AggregationType.CUSTOM_INCIDENT_TYPE]


@mock.patch('pager_duty_stats.main.fetch_all_incidents')
@mock.patch('pager_duty_stats.main.print_statistics')
@mock.patch('pager_duty_stats.main.get_stats')
@mock.patch('pager_duty_stats.main.get_pager_duty_api_key')
def test_run_smoke(
    mock_get_pager_duty_api_key,
    mock_get_stats,
    mock_print_statistics,
    mock_fetch_all_incidents
):
    mock_stats = mock.Mock()
    mock_get_stats.return_value = mock_stats
    run([
        '--service-ids', 'service A', 'service B',
        '--start-date', '2020-01-01',
        '--end-date', '2020-02-01',
    ])
    mock_print_statistics.assert_called_once_with(
        start_date='2020-01-01',
        end_date='2020-02-01',
        grouping_window=GroupingWindow.WEEK,
        stats=mock_stats,
        aggregation_types=[AggregationType.SERVICE_NAME]
    )
