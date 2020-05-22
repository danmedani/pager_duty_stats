import sys
import json
from csv import DictWriter
from typing import List
from typing import Dict
from typing import Set
from datetime import datetime
from datetime import timedelta
from pager_duty_stats.logic.aggregation import AggregrateStats
from pager_duty_stats.logic.aggregation import AggregationType
from pager_duty_stats.logic.aggregation import get_earlist_date
from pager_duty_stats.logic.aggregation import GroupingWindow
from pager_duty_stats.logic.util.dates import step_through_dates

def get_aggregation_type_values(
	stats: Dict[str, AggregrateStats],
	aggregation_types: List[AggregationType]
) ->  Dict[AggregationType, List[str]]:
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


def get_header_fieldnames(
	output_date_col_name: str,
	aggregation_types: List[AggregationType],
	aggregation_type_values: Dict[AggregationType, List[str]]
):
	fieldnames = [output_date_col_name, 'Total Pages']
	
	for aggregation_type in aggregation_types:
		for value in aggregation_type_values[aggregation_type]:
			fieldnames.append(value)

	return fieldnames


def print_statistics(
	start_date: str,
	end_date: str,
	grouping_window: GroupingWindow,
	stats: Dict[str, AggregrateStats],
	aggregation_types: List[AggregationType]
) -> None:
	output_date_col_name = str(grouping_window).capitalize()
	aggregation_type_values = get_aggregation_type_values(stats, aggregation_types)
	
	writer = DictWriter(
		sys.stdout, 
		fieldnames=get_header_fieldnames(
			output_date_col_name, 
			aggregation_types, 
			aggregation_type_values
		), 
		delimiter='\t'
	)
	writer.writeheader()

	for date in step_through_dates(start_date, end_date):
		if date in stats:
			row_dict = {
				output_date_col_name: date,
				'Total Pages': stats[date]['total_pages'],
			}

			for aggregation_type in aggregation_types:
				for aggregation_type_name in aggregation_type_values[aggregation_type]:
					row_dict[aggregation_type_name] = stats[date]['aggregations'][aggregation_type][aggregation_type_name]

			writer.writerow(row_dict)
