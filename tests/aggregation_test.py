from datetime import datetime
from datetime import timezone

from pager_duty_stats.aggregation import is_high_urgency
from pager_duty_stats.aggregation import is_week_day

def test_is_not_high_urgency():
	assert not is_high_urgency({'service': {'summary': 'Yelp Connect LOW Urgency'}})

def test_is_high_urgency():
	assert is_high_urgency({'service': {'summary': 'Yelp Connect CRITICAL Urgency'}})

def test_is_week_day_friday_pre_furlough():
	assert is_week_day(datetime.strptime('2020-04-10', '%Y-%m-%d').replace(tzinfo=timezone.utc))

def test_is_week_day_friday_post_furlough():
	assert not is_week_day(datetime.strptime('2020-05-01', '%Y-%m-%d').replace(tzinfo=timezone.utc))

def test_is_saturday_week_day():
	assert not is_week_day(datetime.strptime('2020-05-17', '%Y-%m-%d').replace(tzinfo=timezone.utc))
