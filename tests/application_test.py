import mock

from pager_duty_stats.application import get_index
from pager_duty_stats.application import get_stats


@mock.patch('pager_duty_stats.application.application')
def test_get_index(
    mock_application
):
    get_index()
    mock_application.send_static_file.assert_called_once_with('index.html')


@mock.patch('pager_duty_stats.application.application')
def test_get_stats(
    mock_application
):
    get_stats()
    mock_application.send_static_file.assert_called_once_with('stats.html')
