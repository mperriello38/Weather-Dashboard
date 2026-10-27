from unittest.mock import Mock

import pytest
import requests

from weather_dashboard import openweather


@pytest.mark.parametrize(
    ("api_key", "expected_error"),
    [
        ("", ValueError),
        ("  ", ValueError),
        (0, TypeError),
        (0.1, TypeError),
        (True, TypeError),
    ],
)
def test_client_rejects_invalid_key(api_key, expected_error):
    with pytest.raises(expected_error):
        temp_client = openweather.OpenWeatherClient(api_key, "imperial", 10)


@pytest.mark.parametrize(
    ("units", "expected_error"),
    [
        ("", ValueError),
        ("IMPERIAL", ValueError),
        ("metric ", ValueError),
        (3, TypeError),
    ],
)
def test_client_rejects_invalid_units(units, expected_error):
    with pytest.raises(expected_error):
        temp_client = openweather.OpenWeatherClient("test-api-key", units, 10)


@pytest.mark.parametrize(
    ("timeout", "expected_error"),
    [
        (-1, ValueError),
        (0, ValueError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (float("-inf"), ValueError),
        (True, TypeError),
        ("", TypeError),
    ],
)
def test_client_rejects_invalid_timeout(timeout, expected_error):
    with pytest.raises(expected_error):
        temp_client = openweather.OpenWeatherClient("test-api-key", "imperial", timeout)


@pytest.fixture
def client():
    return openweather.OpenWeatherClient(
        api_key="test-api-key", units="metric", timeout=3
    )


def test_search_locations_sends_expected_request(client, monkeypatch):
    expected_locations = [
        {
            "name": "Chicago",
            "state": "Illinois",
            "country": "US",
            "lat": 41.88,
            "lon": -87.63,
        }
    ]

    fake_response = Mock()
    fake_response.json.return_value = expected_locations

    fake_get = Mock(return_value=fake_response)

    monkeypatch.setattr(openweather.requests, "get", fake_get)

    result = client.search_locations("Chicago,US", limit=1)

    assert result == expected_locations

    fake_get.assert_called_once_with(
        openweather.GEOCODING_URL,
        params={
            "q": "Chicago,US",
            "appid": "test-api-key",
            "limit": 1,
        },
        timeout=3,
    )

    fake_response.raise_for_status.assert_called_once_with()


def test_search_locations_converts_invalid_json(client, monkeypatch):
    decode_error = requests.exceptions.JSONDecodeError("bad JSON", "", 0)

    fake_response = Mock()
    fake_response.json.side_effect = decode_error

    monkeypatch.setattr(openweather.requests, "get", Mock(return_value=fake_response))

    with pytest.raises(
        openweather.OpenWeatherResponseError, match="unreadable JSON"
    ) as exception_info:
        client.search_locations("Chicago")

    assert exception_info.value.__cause__ is decode_error


def test_search_locations_converts_timeout(client, monkeypatch):
    original_error = requests.Timeout("Too slow")
    fake_get = Mock(side_effect=original_error)

    monkeypatch.setattr(openweather.requests, "get", fake_get)

    with pytest.raises(
        openweather.OpenWeatherTimeoutError, match="timed out"
    ) as exception_info:
        client.search_locations("Chicago")

    assert exception_info.value.__cause__ is original_error


def test_search_locations_converts_http_error(client, monkeypatch):
    fake_response = Mock()
    fake_response.status_code = 401
    original_error = requests.HTTPError("Unauthorized")
    fake_response.raise_for_status.side_effect = original_error

    monkeypatch.setattr(openweather.requests, "get", Mock(return_value=fake_response))

    with pytest.raises(openweather.OpenWeatherHTTPError) as exception_info:
        client.search_locations("Chicago")

    assert exception_info.value.status_code == 401
    assert str(exception_info.value) == "OpenWeather returned HTTP 401."

    assert exception_info.value.__cause__ is original_error


def test_search_locations_converts_connection_error(client, monkeypatch):
    original_error = requests.ConnectionError("Can't connect")
    fake_get = Mock(side_effect=original_error)

    monkeypatch.setattr(openweather.requests, "get", fake_get)

    with pytest.raises(
        openweather.OpenWeatherConnectionError, match="Could not connect"
    ) as exception_info:
        client.search_locations("Chicago")

    assert exception_info.value.__cause__ is original_error


def test_search_locations_converts_unexpected_error(client, monkeypatch):
    original_error = requests.RequestException("Unknown error")
    fake_get = Mock(side_effect=original_error)

    monkeypatch.setattr(openweather.requests, "get", fake_get)

    with pytest.raises(
        openweather.OpenWeatherError, match="unexpected request"
    ) as exception_info:
        client.search_locations("Chicago")

    assert exception_info.value.__cause__ is original_error


@pytest.mark.parametrize(
    ("query"),
    [
        " Chicago,IL,US",
        "Chicago ,IL,US",
        "  Chicago  , IL, US",
        "Chicago,IL , US",
    ],
)
def test_search_locations_trims_query(client, monkeypatch, query):
    expected_locations = [
        {
            "name": "Chicago",
            "state": "Illinois",
            "country": "US",
            "lat": 41.88,
            "lon": -87.63,
        }
    ]

    expected_params = {"q": "Chicago,IL,US", "appid": "test-api-key", "limit": 1}

    fake_response = Mock()
    fake_response.json.return_value = expected_locations

    fake_get = Mock(return_value=fake_response)
    monkeypatch.setattr(openweather.requests, "get", fake_get)

    result = client.search_locations(query, limit=1)

    assert result == expected_locations

    fake_get.assert_called_once_with(
        openweather.GEOCODING_URL, params=expected_params, timeout=3
    )


def test_get_current_weather_sends_expected_request(client, monkeypatch):
    expected_weather = {
        "coord": {
            "lon": -87.63,
            "lat": 41.88,
        },
        "weather": [
            {
                "id": 800,
                "main": "Clear",
                "description": "clear sky",
                "icon": "01d",
            }
        ],
        "main": {
            "temp": 13.27,
            "feels_like": 12.14,
            "temp_min": 11.67,
            "temp_max": 14.44,
            "pressure": 1024,
            "humidity": 58,
        },
        "visibility": 10000,
        "wind": {
            "speed": 3.6,
            "deg": 70,
        },
        "clouds": {
            "all": 0,
        },
        "dt": 1777449371,
        "sys": {
            "country": "US",
            "sunrise": 1777437375,
            "sunset": 1777490344,
        },
        "timezone": -18000,
        "name": "Chicago",
        "cod": 200,
    }

    fake_response = Mock()
    fake_response.json.return_value = expected_weather

    fake_get = Mock(return_value=fake_response)

    monkeypatch.setattr(openweather.requests, "get", fake_get)

    result = client.get_current_weather(41.88, -87.63)

    assert result == expected_weather

    fake_get.assert_called_once_with(
        openweather.CURRENT_WEATHER_URL,
        params={
            "lat": 41.88,
            "lon": -87.63,
            "appid": "test-api-key",
            "units": "metric",
        },
        timeout=3,
    )

    fake_response.raise_for_status.assert_called_once_with()


def test_get_current_weather_converts_invalid_json(client, monkeypatch):
    decode_error = requests.exceptions.JSONDecodeError("bad JSON", "", 0)

    fake_response = Mock()
    fake_response.json.side_effect = decode_error

    monkeypatch.setattr(openweather.requests, "get", Mock(return_value=fake_response))

    with pytest.raises(
        openweather.OpenWeatherResponseError, match="unreadable JSON"
    ) as exception_info:
        client.get_current_weather(41.88, -87.63)

    assert exception_info.value.__cause__ is decode_error


def test_get_current_weather_converts_timeout(client, monkeypatch):
    original_error = requests.Timeout("Too slow")
    fake_get = Mock(side_effect=original_error)

    monkeypatch.setattr(openweather.requests, "get", fake_get)

    with pytest.raises(
        openweather.OpenWeatherTimeoutError, match="timed out"
    ) as exception_info:
        client.get_current_weather(41.88, -87.63)

    assert exception_info.value.__cause__ is original_error


def test_get_current_weather_converts_http_error(client, monkeypatch):
    fake_response = Mock()
    fake_response.status_code = 401
    original_error = requests.HTTPError("Unauthorized")
    fake_response.raise_for_status.side_effect = original_error

    monkeypatch.setattr(openweather.requests, "get", Mock(return_value=fake_response))

    with pytest.raises(openweather.OpenWeatherHTTPError) as exception_info:
        client.get_current_weather(41.88, -87.63)

    assert exception_info.value.status_code == 401
    assert str(exception_info.value) == "OpenWeather returned HTTP 401."

    assert exception_info.value.__cause__ is original_error


def test_get_current_weather_converts_connection_error(client, monkeypatch):
    original_error = requests.ConnectionError("Can't connect")
    fake_get = Mock(side_effect=original_error)

    monkeypatch.setattr(openweather.requests, "get", fake_get)

    with pytest.raises(
        openweather.OpenWeatherConnectionError, match="Could not connect"
    ) as exception_info:
        client.get_current_weather(41.88, -87.63)

    assert exception_info.value.__cause__ is original_error


def test_get_current_weather_converts_unexpected_error(client, monkeypatch):
    original_error = requests.RequestException("Unknown error")
    fake_get = Mock(side_effect=original_error)

    monkeypatch.setattr(openweather.requests, "get", fake_get)

    with pytest.raises(
        openweather.OpenWeatherError, match="unexpected request"
    ) as exception_info:
        client.get_current_weather(41.88, -87.63)

    assert exception_info.value.__cause__ is original_error


@pytest.mark.parametrize(
    ("limit", "expected_error"),
    [
        (0, ValueError),
        (6, ValueError),
        (True, TypeError),
        ("5", TypeError),
    ],
)
def test_search_locations_rejects_invalid_limit(
    client, monkeypatch, limit, expected_error
):
    fake_get = Mock()
    monkeypatch.setattr(openweather.requests, "get", fake_get)

    with pytest.raises(expected_error):
        client.search_locations("Chicago", limit=limit)

    fake_get.assert_not_called()


@pytest.mark.parametrize(
    ("query", "expected_error"),
    [
        ("", ValueError),
        ("  ", ValueError),
        (0, TypeError),
        (0.1, TypeError),
        (True, TypeError),
    ],
)
def test_search_locations_rejects_invalid_query(
    client, monkeypatch, query, expected_error
):
    fake_get = Mock()
    monkeypatch.setattr(openweather.requests, "get", fake_get)

    with pytest.raises(expected_error):
        client.search_locations(query)

    fake_get.assert_not_called()


@pytest.mark.parametrize(
    ("latitude", "longitude", "expected_error"),
    [
        (-90.1, 0, ValueError),
        (90.1, 0, ValueError),
        (-91, 0, ValueError),
        (100, 0, ValueError),
        (0, -180.1, ValueError),
        (14, 184, ValueError),
        (0, float("nan"), ValueError),
        (0, float("inf"), ValueError),
        (0, float("-inf"), ValueError),
        (float("nan"), 0, ValueError),
        (float("inf"), 0, ValueError),
        (float("-inf"), 0, ValueError),
        (True, 0, TypeError),
        (0, False, TypeError),
        ("", 0, TypeError),
        (0, "", TypeError),
    ],
)
def test_get_current_weather_rejects_invalid_coordinates(
    client, monkeypatch, latitude, longitude, expected_error
):
    fake_get = Mock()
    monkeypatch.setattr(openweather.requests, "get", fake_get)

    with pytest.raises(expected_error):
        client.get_current_weather(latitude, longitude)

    fake_get.assert_not_called()


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        (-90, -180),
        (90, 180),
        (90, -180),
        (-90, 180),
    ],
)
def test_get_current_weather_accepts_maximum_coordinates(
    client, monkeypatch, latitude, longitude
):
    expected_weather = {
        "coord": {
            "lon": longitude,
            "lat": latitude,
        },
        "weather": [
            {
                "id": 800,
                "main": "Clear",
                "description": "clear sky",
                "icon": "01d",
            }
        ],
        "main": {
            "temp": 13.27,
            "feels_like": 12.14,
            "temp_min": 11.67,
            "temp_max": 14.44,
            "pressure": 1024,
            "humidity": 58,
        },
        "visibility": 10000,
        "wind": {
            "speed": 3.6,
            "deg": 70,
        },
        "clouds": {
            "all": 0,
        },
        "dt": 1777449371,
        "sys": {
            "country": "US",
            "sunrise": 1777437375,
            "sunset": 1777490344,
        },
        "timezone": -18000,
        "name": "Chicago",
        "cod": 200,
    }

    fake_response = Mock()

    fake_response.json.return_value = expected_weather

    fake_get = Mock(return_value=fake_response)

    monkeypatch.setattr(openweather.requests, "get", fake_get)

    assert client.get_current_weather(latitude, longitude) == expected_weather

    fake_get.assert_called_once_with(
        openweather.CURRENT_WEATHER_URL,
        params={
            "lat": latitude,
            "lon": longitude,
            "appid": "test-api-key",
            "units": "metric",
        },
        timeout=3,
    )
