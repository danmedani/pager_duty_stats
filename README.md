# pager_duty_stats
Gathering and Aggregating Pager Duty Statistics

This library aggregates pager duty statistics for a list of teams and outputs tab-separated csv. 

It has a couple cool features:
1. Ability to aggregate by day or by week across a date range. See `--grouping-window`, `--start-date` and `--end-date` options.
2. Includes a break-down of when pages are happening (during work-hours, during off hours, or during sleep hours). See `--include-time-of-day-counts` option.
3. Can include groupings of the most common error types that are happening. See `--include-incident-types`, `--max-incident-types`, and `--incident-type-extraction-technique` options.

I usually just pipe the output into a file and import it into google sheets to get nice visuals.

# API Token
1. Generate an api token from PagerDuty (My Profile -> User Settings -> Create API User Token)
2. Stick it in a file in the main directory of this repo called `.api_key` (this is the default place it's looked for - feel free to put it whereever and specify the path with a `--pd-key-file` option).

# Building
1. `make build`
2. `source virtual_env/bin/activate` (todo: can this be done from the Makefile?)

# Testing (need to be in virtual env)
1. `make test`

# Fetching & Aggregating Stats

This outputs a tab-seperated csv. 

After running `source virtual_env/bin/activate`, here's an example using all the options:

```
python -m pager_duty_stats.main \
	--pd-key-file .api_key \
	--grouping-window day \
	--service_ids G289YKF R289YKF \
	--start-date 2020-01-01 \
	--end-date 2020-04-01 \
	--include-time-of-day-counts \
	--include-incident-types \
	--max-incident-types 3 \
	--incident-type-extraction-technique title
```

To see more information about the options:
```
python -m pager_duty_stats.main --help
```
