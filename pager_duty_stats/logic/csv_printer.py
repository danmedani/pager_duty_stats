import csv
import sys
from typing import Dict
from datetime import datetime
from datetime import timedelta
from pager_duty_stats.logic.aggregation import AggregrateStats
from pager_duty_stats.logic.aggregation import get_earlist_date


def print_statistics(
	date_col: str,
	stats: Dict[str, AggregrateStats]
) -> None:

	# Header
	all_incident_types_set = set()
	all_services_set = set()
	all_times_of_day_set = set()
	earliest_date = get_earlist_date(list(stats.keys()))
	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date <= datetime.now():
		date_str = str(current_date.date())
		if date_str in stats:
			for service, _ in stats[date_str]['per_service'].items():
				all_services_set.add(service)

			for time_of_day, _ in stats[date_str]['per_time_of_day'].items():
				all_times_of_day_set.add(time_of_day)

			for error_type, _ in stats[date_str]['error_type_counts'].items():
				all_incident_types_set.add(error_type)

		current_date += timedelta(days=1)

	all_incident_types = list(all_incident_types_set)
	all_services = list(all_services_set)
	all_times_of_day = list(all_times_of_day_set)

	fieldnames = [date_col, 'Total Pages']

	for service in all_services:
		fieldnames.append(service)
	for time_of_day in all_times_of_day:
		fieldnames.append(time_of_day)
	for error_type in all_incident_types:
		fieldnames.append(error_type)

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

			for service in all_services:
				row_dict[service] = str(stats[date_str]['per_service'][service]) if service in stats[date_str]['per_service'] else '0'

			for time_of_day in all_times_of_day:
				row_dict[time_of_day] = str(stats[date_str]['per_time_of_day'][time_of_day]) if time_of_day in stats[date_str]['per_time_of_day'] else '0'

			for error_type in all_incident_types:
				row_dict[error_type] = str(stats[date_str]['error_type_counts'][error_type]) if error_type in stats[date_str]['error_type_counts'] else '0'

			writer.writerow(row_dict)
		current_date += timedelta(days=1)






