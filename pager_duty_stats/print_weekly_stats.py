import sys
from pager_duty_stats.pager_duty_client import fetch_all_incidents
from pager_duty_stats.aggregation import get_stats_by_week
from pager_duty_stats.csv_printer import print_stats

if __name__ == "__main__":
	pager_duty_offset = int(sys.argv[1])
	print_stats(
		date_col='Week',
		stats=get_stats_by_week(
			fetch_all_incidents(pager_duty_offset)
		)
	)
