import sys
from pager_duty_stats.pager_duty_client import fetch_all_incidents
from pager_duty_stats.aggregation import get_stats_by_week
from pager_duty_stats.csv_printer import print_stats
import argparse


def get_api_key(file_name: str) -> str:
	with open(file_name, 'r') as file:
		return file.readlines()[0].rstrip('\n')


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Aggregate PagerDuty Stats & output csv')
	parser.add_argument('--pd-key-file', help='File containing API Key to access api.pagerduty.com')
	parser.add_argument('--start-date', help='Date to collect alerts from')
	parser.add_argument('--end-date', help='Date to collect alerts until')
	options = parser.parse_args(sys.argv[1:])
	
	incidents = fetch_all_incidents(
		pd_api_key=get_api_key(options.pd_key_file),
		start_date=options.start_date,
		end_date=options.end_date
	)

	print_stats(
		date_col='Week',
		stats=get_stats_by_week(
			fetch_all_incidents(
				pd_api_key=get_api_key(options.pd_key_file),
				start_date=options.start_date,
				end_date=options.end_date
			),
			10
		)
	)

