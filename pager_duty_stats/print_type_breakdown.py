import sys
import json
from pager_duty_stats.pager_duty_client import fetch_all_incidents

if __name__ == "__main__":
	pager_duty_offset = int(sys.argv[1])
	incidents = fetch_all_incidents(pager_duty_offset)
	type_map = {}
	for incident in incidents:
		types = incident['title'].split(' : ')
		if len(types) > 1:
			the_type = types[1]
		else:
			the_type[0]
		if the_type not in type_map:
			type_map[the_type] = 0
		type_map[the_type] += 1

	errors_and_types = [(key, val) for key, val in type_map.items()]
	sorted_errors_and_types = sorted(errors_and_types, key=lambda pair: -1 * pair[1])
	for gg in sorted_errors_and_types:
		if gg[1] > 5:
			print(gg)

# title, description, summary