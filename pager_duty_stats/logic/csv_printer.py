import csv
import sys
import json
from typing import List
from typing import Dict
from datetime import datetime
from datetime import timedelta
from pager_duty_stats.logic.aggregation import AggregrateStats
from pager_duty_stats.logic.aggregation import get_earlist_date


def print_statistics(
	date_col: str,
	stats: Dict[str, AggregrateStats],
	aggregation_groups: List[str]
) -> None:

	# Header
	all_incident_types_set = set()
	all_services_set = set()
	all_times_of_day_set = set()

	all_aggregation_group_names = {
		aggregation_group: set()
		for aggregation_group in aggregation_groups
	}

	earliest_date = get_earlist_date(list(stats.keys()))
	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date <= datetime.now():
		date_str = str(current_date.date())

		if date_str in stats:
			for aggregation_group in aggregation_groups:
				for name, _ in stats[date_str]['aggregations'][aggregation_group].items():
					all_aggregation_group_names[aggregation_group].add(name)

		current_date += timedelta(days=1)

	fieldnames = [date_col, 'Total Pages']

	all_aggregation_group_lists = {
		aggregation_group: list(all_aggregation_group_names[aggregation_group])
		for aggregation_group in aggregation_groups
	}
	
	for aggregation_group in aggregation_groups:
		for aggregation_group_name in all_aggregation_group_lists[aggregation_group]:
			fieldnames.append(aggregation_group_name)

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

			for aggregation_group in aggregation_groups:
				for aggregation_group_name in all_aggregation_group_lists[aggregation_group]:
					row_dict[aggregation_group_name] = stats[date_str]['aggregations'][aggregation_group][aggregation_group_name]

			writer.writerow(row_dict)
		current_date += timedelta(days=1)






