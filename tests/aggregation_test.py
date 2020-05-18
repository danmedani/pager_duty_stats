from datetime import datetime
from datetime import timezone

from pager_duty_stats.aggregation import is_week_day

def test_is_mon_week_day():
	assert is_week_day(datetime.strptime('2020-05-18', '%Y-%m-%d').replace(tzinfo=timezone.utc))

def test_is_sun_week_day():
	assert not is_week_day(datetime.strptime('2020-05-17', '%Y-%m-%d').replace(tzinfo=timezone.utc))

def test_is_sat_week_day():
	assert not is_week_day(datetime.strptime('2020-05-16', '%Y-%m-%d').replace(tzinfo=timezone.utc))
