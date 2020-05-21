import argparse
import sys

from datetime import datetime
from pager_duty_stats.logic.pager_duty_client import fetch_all_incidents
from pager_duty_stats.logic.aggregation import get_stats
from pager_duty_stats.logic.csv_printer import print_statistics
from pager_duty_stats.logic.aggregation import GroupingWindow
from pager_duty_stats.logic.incident_types import ExtractionTechnique
from argparse import Namespace


def get_pager_duty_api_key(file_name: str) -> str:
	with open(file_name, 'r') as file:
		return file.readlines()[0].rstrip('\n')

def parse_args() -> Namespace:
	parser = argparse.ArgumentParser(description='Aggregate PagerDuty stats & output a csv')
	
	parser.add_argument('--pd-key-file', default='.api_key', help='File containing API Key to access api.pagerduty.com (default .api_key)')
	parser.add_argument('--service_ids', required=True, type=str, nargs='+', help='PD service ids to collect stats on')
	parser.add_argument('--start-date', required=True, help='Date to collect alerts from (YYYY-MM-DD)')
	parser.add_argument('--end-date', default=str(datetime.now().date()), help='Date to collect alerts until (YYYY-MM-DD) (default: todays date)')
	parser.add_argument('--grouping-window', default=GroupingWindow.WEEK, type=GroupingWindow, choices=list(GroupingWindow), help='Group alerts by day, or by week? If by week, this only collects complete weeks (from Monday -> Sunday)')
	
	parser.add_argument('--include-time-of-day-counts', action='store_true', default=False, help='Includes breakdown of what time (work hours, off hours, sleep hours) errors are happening')

	parser.add_argument('--include-incident-types', action='store_true', default=False, help='Includes breakdown of the types of errors that are happening')
	parser.add_argument('--incident-type-extraction-technique', default=ExtractionTechnique.YC, type=ExtractionTechnique, choices=list(ExtractionTechnique), help='Technique for reducing/classifying incidents (for use with --include-incident-types). See pager_duty_stats.logic.incident_types for more details')
	parser.add_argument('--max-incident-types', type=int, default=10, help='(For use with --include-incident-types): this determines how many of the most common incident types to show. (default: 10)')
	
	return parser.parse_args(sys.argv[1:])


if __name__ == "__main__":
	options = parse_args()

	incidents = fetch_all_incidents(
		pd_api_key=get_pager_duty_api_key(options.pd_key_file),
		service_ids=options.service_ids,
		start_date=options.start_date,
		end_date=options.end_date
	)

	print_statistics(
		date_col=str(options.grouping_window).capitalize(),
		stats=get_stats(
			incidents=incidents,
			start_date=options.start_date,
			end_date=options.end_date,
			grouping_window=options.grouping_window,
			incident_type_extraction_technique=options.incident_type_extraction_technique,
			max_incident_types=options.max_incident_types,
			aggregation_groups=['per_service', 'per_time_of_day', 'custom_incident_type']
		),
		aggregation_groups=['per_service', 'per_time_of_day', 'custom_incident_type']
	)

