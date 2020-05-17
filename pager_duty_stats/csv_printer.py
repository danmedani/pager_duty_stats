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
	print('{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
		date_col,
		'Total Pages',
		'Low Urgency',
		'High Urgency',
		'Work Hour Pages',
		'Leisure Hour Pages',
		'Wake up Pages'
	))

	earliest_date = get_earlist_date(stats.keys())
	current_date = datetime.strptime(earliest_date, '%Y-%m-%d')
	while current_date <= datetime.now():
		date_str = str(current_date.date())
		if date_str in stats:
			print(
				'{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
					date_str,
					stats[date_str]['total_pages'],
					stats[date_str]['low_urgency'],
					stats[date_str]['high_urgency'],
					stats[date_str]['work_hour'],
					stats[date_str]['leisure_hour'],
					stats[date_str]['sleep_hour']
				)
			)
		current_date += timedelta(days=1)
