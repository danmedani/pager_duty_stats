import pytest
import mock
from pager_duty_stats.logic.csv_printer import get_aggregation_type_values
from pager_duty_stats.logic.csv_printer import get_header_fieldnames
from pager_duty_stats.logic.csv_printer import print_statistics
from collections import defaultdict
from pager_duty_stats.logic.aggregation import AggregationType
from pager_duty_stats.logic.aggregation import AggregrateStats
from pager_duty_stats.logic.aggregation import GroupingWindow


@pytest.fixture
def mock_stats():
    return {
        '2020-01-01': AggregrateStats(
            total_pages=14,
            aggregations={
                AggregationType.SERVICE_NAME: defaultdict(int, **{'service A': 4, 'service B': 10}),
                AggregationType.TIME_OF_DAY: defaultdict(int, **{'work': 13, 'sleep': 1})
            }
        ),
        '2020-01-02': AggregrateStats(
            total_pages=5,
            aggregations={
                AggregationType.SERVICE_NAME: defaultdict(int, **{'service B': 4, 'service C': 1}),
                AggregationType.TIME_OF_DAY: defaultdict(int, ** {'leisure': 5})
            }
        )
    }


@mock.patch('pager_duty_stats.logic.csv_printer.DictWriter')
def test_print_statistics_smoke_test(
    mock_DictWriter,
    mock_stats
):
    print_statistics(
        grouping_window=GroupingWindow.WEEK,
        stats=mock_stats,
        aggregation_types=[AggregationType.SERVICE_NAME, AggregationType.TIME_OF_DAY]
    )
    mock_DictWriter.assert_called_once_with(
        mock.ANY,
        fieldnames=mock.ANY, # see test_get_header_fieldnames
        delimiter='\t'
    )


def test_get_header_fieldnames():
    assert get_header_fieldnames(
        output_date_col_name='Week',
        aggregation_types=[
            AggregationType.TIME_OF_DAY, 
            AggregationType.SERVICE_NAME
        ],
        aggregation_type_values={
            AggregationType.SERVICE_NAME: ['service A', 'service B', 'service C'],
            AggregationType.TIME_OF_DAY: ['work', 'sleep', 'leisure']
        }
    ) == ['Week', 'Total Pages', 'work', 'sleep', 'leisure', 'service A', 'service B', 'service C']

def test_get_header_fieldnames_different_order():
    assert get_header_fieldnames(
        output_date_col_name='Week',
        aggregation_types=[
            AggregationType.SERVICE_NAME,
            AggregationType.TIME_OF_DAY
        ],
        aggregation_type_values={
            AggregationType.SERVICE_NAME: ['service A', 'service B', 'service C'],
            AggregationType.TIME_OF_DAY: ['leisure', 'sleep', 'work']
        }
    ) == ['Week', 'Total Pages', 'service A', 'service B', 'service C', 'leisure', 'sleep', 'work']


def test_get_aggregation_type_values(
    mock_stats
):
    assert get_aggregation_type_values(
        stats=mock_stats,
        aggregation_types=[AggregationType.TIME_OF_DAY, AggregationType.SERVICE_NAME]
    ) == {
        AggregationType.SERVICE_NAME: ['service A', 'service B', 'service C'],
        AggregationType.TIME_OF_DAY: ['leisure', 'sleep', 'work']
    }
