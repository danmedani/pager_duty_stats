from collections import defaultdict

import pytest

from pager_duty_stats.formatter.series import get_aggregation_type_values
from pager_duty_stats.logic.aggregation import AggregationType
from pager_duty_stats.logic.aggregation import AggregrateStats


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
