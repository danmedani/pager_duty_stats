from datetime import datetime
from datetime import timedelta
from typing import Generator
from typing import Tuple

DATE_RANGE_CHUNK_DAYS = 30


def step_through_dates(
    start_date: str,
    end_date: str
) -> Generator[str, None, None]:
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    last_date = datetime.strptime(end_date, '%Y-%m-%d')
    while current_date <= last_date:
        yield str(current_date.date())
        current_date += timedelta(days=1)


def step_through_date_range_chunks(
    start_date: str,
    end_date: str
) -> Generator[Tuple[str, str], None, None]:
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    last_date = datetime.strptime(end_date, '%Y-%m-%d')
    while current_date < last_date:
        yield (str(current_date.date()), str(min(current_date + timedelta(days=DATE_RANGE_CHUNK_DAYS), last_date).date()))
        current_date += timedelta(days=DATE_RANGE_CHUNK_DAYS)
