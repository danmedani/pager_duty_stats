import csv
import sys
import json
from typing import List
from typing import Dict
from typing import Set
from datetime import datetime
from datetime import timedelta
from pager_duty_stats.logic.aggregation import AggregrateStats
from pager_duty_stats.logic.aggregation import AggregationType
from pager_duty_stats.logic.aggregation import get_earlist_date


def print_statistics(
	date_col: str,
	stats: Dict[str, AggregrateStats],
	aggregation_types: List[AggregationType]
) -> None:

	# Header
	all_aggregation_type_names: Dict[AggregationType, Set[str]] = {
		aggregation_type: set()
		for aggregation_type in aggregation_types
	}

	earliest_date = get_earlist_date(list(stats.keys()))
	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date <= datetime.now():
		date_str = str(current_date.date())

		if date_str in stats:
			for aggregation_type in aggregation_types:
				for name, _ in stats[date_str]['aggregations'][aggregation_type].items():
					all_aggregation_type_names[aggregation_type].add(name)

		current_date += timedelta(days=1)

	fieldnames = [date_col, 'Total Pages']

	all_aggregation_type_lists = {
		aggregation_type: list(all_aggregation_type_names[aggregation_type])
		for aggregation_type in aggregation_types
	}
	
	for aggregation_type in aggregation_types:
		for aggregation_type_name in all_aggregation_type_lists[aggregation_type]:
			fieldnames.append(aggregation_type_name)

	writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter='\t')
	writer.writeheader()

	earliest_date = get_earlist_date(list(stats.keys()))
	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date <= datetime.now():
		date_str = str(current_date.date())
		if date_str in stats:
			row_dict = {
				date_col: date_str,
				'Total Pages': stats[date_str]['total_pages'],
			}

			for aggregation_type in aggregation_types:
				for aggregation_type_name in all_aggregation_type_lists[aggregation_type]:
					row_dict[aggregation_type_name] = stats[date_str]['aggregations'][aggregation_type][aggregation_type_name]

			writer.writerow(row_dict)
		current_date += timedelta(days=1)






