from datetime import datetime
import sys
from pager_duty_stats.pager_duty_client import fetch_all_incidents
from pager_duty_stats.aggregation import get_stats
from pager_duty_stats.csv_printer import print_stats
from pager_duty_stats.aggregation import GroupingWindow
import argparse

DEFAULT_START_DATE = '2010-01-01'

GROUPING_WINDOW_HELP = '''
Group alerts by day, or by week? If by week, this only collects complete weeks (from Monday -> Sunday)
'''

def get_api_key(file_name: str) -> str:
	with open(file_name, 'r') as file:
		return file.readlines()[0].rstrip('\n')

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Aggregate PagerDuty stats & output a csv')

	parser.add_argument('--pd-key-file', default='.api_key', help='File containing API Key to access api.pagerduty.com')
	parser.add_argument('--start-date', default=DEFAULT_START_DATE, help='Date to collect alerts from')
	parser.add_argument('--end-date', default=str(datetime.now().date()), help='Date to collect alerts until (default: today)')
	parser.add_argument('--service_ids', required=True, type=str, nargs='+', help='PD service ids to collect stats on')
	parser.add_argument('--grouping-window', default='week', type=GroupingWindow, choices=list(GroupingWindow), help=GROUPING_WINDOW_HELP)
	parser.add_argument('--max-error-types', type=int, default=10, help='Max number of types to group by')
	
	options = parser.parse_args(sys.argv[1:])
	
	incidents = fetch_all_incidents(
		pd_api_key=get_api_key(options.pd_key_file),
		service_ids=options.service_ids,
		start_date=options.start_date,
		end_date=options.end_date
	)

	print_stats(
		date_col=str(options.grouping_window).capitalize(),
		stats=get_stats(
			incidents,
			options.max_error_types,
			options.grouping_window
		)
	)

