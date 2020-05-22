from datetime import datetime
from datetime import timedelta
from typing import Generator


def step_through_dates(
    start_date: str,
    end_date: str
) -> Generator[str, None, None]:
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    last_date = datetime.strptime(end_date, '%Y-%m-%d')
    while current_date <= last_date:
        yield str(current_date.date())
        current_date += timedelta(days=1)
