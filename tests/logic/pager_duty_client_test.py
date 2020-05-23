import mock
import pytest

from pager_duty_stats.logic.pager_duty_client import fetch_all_incidents
from pager_duty_stats.logic.pager_duty_client import fetch_incident_chunk
from pager_duty_stats.logic.pager_duty_client import InvalidApiKeyException
from pager_duty_stats.logic.pager_duty_client import InvalidServiceException


@mock.patch('pager_duty_stats.logic.pager_duty_client.requests')
def test_fetch_incident_chunk_200(
    mock_requests
):
    mock_return_val = {'incidents': [{'title': 'incident A'}]}
    mock_requests.get = mock.Mock()
    mock_requests.get.return_value = mock.Mock(
        status_code=200,
        json=lambda: mock_return_val
    )

    assert fetch_incident_chunk(
        pd_api_key='fake_api_key',
        service_ids=['serviceA', 'serviceB'],
        start_date='2020-01-01',
        end_date='2021-01-02',
        limit=100,
        offset=0
    ) == [{'title': 'incident A'}]
    mock_requests.get.assert_called_once_with(
        'https://api.pagerduty.com/incidents',
        headers={
            'Authorization': 'Token token=fake_api_key',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'From': 'dmedani@yelp.com'
        },
        params={
            'service_ids[]': ['serviceA', 'serviceB'],
            'since': '2020-01-01',
            'until': '2021-01-02',
            'limit': '100',
            'offset': '0'
        }
    )

@mock.patch('pager_duty_stats.logic.pager_duty_client.requests')
def test_fetch_incident_chunk_invalid_service(
    mock_requests
):
    mock_requests.get = mock.Mock()
    mock_requests.get.return_value = mock.Mock(
        status_code=400,
        json=lambda: {'message': 'service not found'}
    )

    with pytest.raises(InvalidServiceException):
        fetch_incident_chunk(
            pd_api_key='fake_api_key',
            service_ids=['serviceA', 'serviceB'],
            start_date='2020-01-01',
            end_date='2021-01-02',
            limit=100,
            offset=0
        ) == [{'title': 'incident A'}]


@mock.patch('pager_duty_stats.logic.pager_duty_client.requests')
def test_fetch_incident_chunk_invalid_api_key(
    mock_requests
):
    mock_requests.get = mock.Mock()
    mock_requests.get.return_value = mock.Mock(
        status_code=404,
        json=lambda: {'message': 'api key invalid'}
    )

    with pytest.raises(InvalidApiKeyException):
        fetch_incident_chunk(
            pd_api_key='fake_api_key',
            service_ids=['serviceA', 'serviceB'],
            start_date='2020-01-01',
            end_date='2021-01-02',
            limit=100,
            offset=0
        ) == [{'title': 'incident A'}]


@mock.patch('pager_duty_stats.logic.pager_duty_client.fetch_incident_chunk')
def test_fetch_all_incidents(
    mock_fetch_incident_chunk
):
    mock_fetch_incident_chunk.side_effect = [
        [
            {'title': 'incident A'},
            {'title': 'incident B'},
            {'title': 'incident C'}
        ],
        [
            {'title': 'incident D'},
            {'title': 'incident E'}
        ],
        []
    ]
    assert fetch_all_incidents(
        pd_api_key='fake_api_key',
        service_ids=['serviceA', 'serviceB'],
        start_date='2020-01-01',
        end_date='2021-01-01'
    ) == [
        {'title': 'incident A'},
        {'title': 'incident B'},
        {'title': 'incident C'},
        {'title': 'incident D'},
        {'title': 'incident E'}
    ]
    mock_fetch_incident_chunk.assert_has_calls([
        mock.call(
            pd_api_key='fake_api_key',
            service_ids=['serviceA', 'serviceB'],
            start_date='2020-01-01',
            end_date='2021-01-02',
            limit=100,
            offset=0
        ),
        mock.call(
            pd_api_key='fake_api_key',
            service_ids=['serviceA', 'serviceB'],
            start_date='2020-01-01',
            end_date='2021-01-02',
            limit=100,
            offset=100
        ),
        mock.call(
            pd_api_key='fake_api_key',
            service_ids=['serviceA', 'serviceB'],
            start_date='2020-01-01',
            end_date='2021-01-02',
            limit=100,
            offset=200
        )
    ])
