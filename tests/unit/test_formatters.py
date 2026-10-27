import pytest

from weather_dashboard import formatters

# Location with a state
# Location without a state
# Multiple locations preserve order
# Empty locations produce []
# Weather description is title-cased
# Temperatures round to one decimal place
# Degree sign and humidity formatting
# Exact multiline summary
fake_geocode_response = [
    {
        "name": "Chicago",
        "state": "Illinois",
        "country": "US",
        "lat": 41.88,
        "lon": -87.63,
    },
    {
        "name": "Fakecago",
        "state": "Fakestate",
        "country": "US",
        "lat": 20.2,
        "lon": 31,
    },
]

fake_weather_response = {
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


def test_format_location_options_preserves_order():
    result = formatters.format_location_options(fake_geocode_response)

    assert result == [
        "Chicago, Illinois, US",
        "Fakecago, Fakestate, US",
    ]


def test_format_location_options_uses_fallback_when_state_is_missing():
    locations = [
        {
            "name": "London",
            "country": "GB",
            "lat": 51.51,
            "lon": -0.13,
        }
    ]

    result = formatters.format_location_options(locations)

    assert result == ["London, No state/region, GB"]


def test_format_location_options_returns_empty_list():
    assert formatters.format_location_options([]) == []


def test_format_current_weather_builds_expected_summary():
    result = formatters.format_current_weather(
        fake_geocode_response[0], fake_weather_response, "metric"
    )

    assert result == (
        "Weather for Chicago, Illinois, US\n"
        "Clear Sky\n"
        "Temperature: 13.3°C\n"
        "Feels like: 12.1°C\n"
        "Humidity: 58%"
    )


def test_format_current_weather_uses_fallback_when_state_is_missing():
    location = {"name": "London", "country": "GB"}

    result = formatters.format_current_weather(
        location, fake_weather_response, "metric"
    )

    assert result.startswith("Weather for London, No state/region, GB\n")


@pytest.mark.parametrize(
    ("units", "expected_error"),
    [
        (2, TypeError),
        ("", ValueError),
        ("unknown", ValueError),
        ("Imperial", ValueError),
    ],
)
def test_format_current_weather_rejects_invalid_units(units, expected_error):
    with pytest.raises(expected_error):
        formatters.format_current_weather(
            fake_geocode_response[0], fake_weather_response, units
        )


@pytest.mark.parametrize(
    ("units", "expected_suffix"),
    [
        ("imperial", "°F"),
        ("metric", "°C"),
        ("standard", "K"),
    ],
)
def test_format_current_weather_uses_expected_temperature_suffix(
    units, expected_suffix
):
    result = formatters.format_current_weather(
        fake_geocode_response[0], fake_weather_response, units
    )

    assert f"Temperature: 13.3{expected_suffix}" in result
    assert f"Feels like: 12.1{expected_suffix}" in result
