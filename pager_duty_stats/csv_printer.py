from typing import Dict
from datetime import datetime
from datetime import timedelta
from pager_duty_stats.aggregation import AggregrateStats
from pager_duty_stats.aggregation import get_earlist_date

def print_stats(
	date_col: str,
	stats: Dict[str, AggregrateStats]
) -> None:

	# Header
	all_error_types_set = set()
	all_services_set = set()
	earliest_date = get_earlist_date(list(stats.keys()))
	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date <= datetime.now():
		date_str = str(current_date.date())
		if date_str in stats:
			for error_type, _ in stats[date_str]['error_type_counts'].items():
				all_error_types_set.add(error_type)

			for service, _ in stats[date_str]['per_service'].items():
				all_services_set.add(service)

		current_date += timedelta(days=1)
	all_error_types = list(all_error_types_set)
	all_services = list(all_services_set)

	header_str = '{}\t{}\t{}\t{}\t{}'.format(
		date_col,
		'Total Pages',
		'Work Hour Pages',
		'Leisure Hour Pages',
		'Wake up Pages'
	)
	for service in all_services:
		header_str = header_str + '\t' + service
	for error_type in all_error_types:
		header_str = header_str + '\t' + error_type
	print(header_str)

	earliest_date = get_earlist_date(list(stats.keys()))
	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date <= datetime.now():
		date_str = str(current_date.date())
		if date_str in stats:
			row_str = '{}\t{}\t{}\t{}\t{}'.format(
				date_str,
				stats[date_str]['total_pages'],
				stats[date_str]['work_hour'],
				stats[date_str]['leisure_hour'],
				stats[date_str]['sleep_hour']
			)
			for service in all_services:
				if service in stats[date_str]['per_service']:
					row_str = row_str + '\t' + str(stats[date_str]['per_service'][service])
				else:
					row_str = row_str + '\t' + '0'
			for error_type in all_error_types:
				if error_type in stats[date_str]['error_type_counts']:
					row_str = row_str + '\t' + str(stats[date_str]['error_type_counts'][error_type])
				else:
					row_str = row_str + '\t' + '0'

			print(row_str)
		current_date += timedelta(days=1)






