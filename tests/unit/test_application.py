import pytest

from unittest.mock import Mock

from weather_dashboard import application


class FakeView:
    def __init__(self, *args):
        self.was_shown = False
        self.results = None
        self.weather = None
        self.error_message = None

    def grid(self):
        self.was_shown = True

    def grid_remove(self):
        self.was_shown = False

    def set_results(self, results):
        self.results = results

    def set_weather(self, weather):
        self.weather = weather

    def set_error_message(self, message):
        self.error_message = message


class FakeRoot:
    def __init__(self, *args):
        self.was_destroyed = False

    def destroy(self):
        self.was_destroyed = True


sample_locations = [
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

sample_weather = {
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


@pytest.fixture
def app_context(monkeypatch):
    for view_name in (
        "WelcomeView",
        "LocationSearchView",
        "LocationResultsView",
        "CurrentWeatherView",
        "ErrorFallbackView",
    ):
        monkeypatch.setattr(application.views, view_name, FakeView)

    root = FakeRoot()

    client = Mock()
    client.units = "imperial"

    app = application.WeatherApp(root, weather_client=client)

    return app, root, client


def test_search_calls_weather_client(app_context):
    app, root, client = app_context

    client.search_locations.return_value = [sample_locations[0]]

    app._handle_begin()
    app._handle_search("Chicago")

    client.search_locations.assert_called_once_with("Chicago")
    assert app.location_results == [sample_locations[0]]
    assert app.location_results_view.results == ["Chicago, Illinois, US"]
    assert app.current_state is application.state_machine.ViewState.LOCATION_RESULTS


def test_handle_location_selected_calls_weather_client(app_context):
    app, root, client = app_context

    client.get_current_weather.return_value = sample_weather

    app.location_results = sample_locations
    app._show_view(application.state_machine.ViewState.LOCATION_RESULTS)

    app._handle_location_selected(1)

    client.get_current_weather.assert_called_once_with(20.2, 31)

    assert app.selected_location == sample_locations[1]
    assert app.current_state is application.state_machine.ViewState.CURRENT_WEATHER


def test_handle_quit_destroys_root(app_context):
    app, root, client = app_context

    app._handle_quit()

    assert app.root.was_destroyed == True


def test_handle_begin_shows_search(app_context):
    app, root, client = app_context

    previous_state = app.current_state
    previous_view = app.views_by_state[previous_state]

    new_state = application.state_machine.ViewState.LOCATION_SEARCH

    app._handle_begin()

    assert app.current_state is new_state
    assert app.views_by_state[new_state].was_shown is True

    if new_state is not previous_state:
        assert previous_view.was_shown is False


def test_show_error_shows_fallback(app_context):
    app, root, client = app_context

    previous_state = app.current_state
    previous_view = app.views_by_state[previous_state]

    new_state = application.state_machine.ViewState.ERROR_FALLBACK

    app._show_error(ValueError("Test error"))

    assert app.current_state is new_state
    assert app.error_fallback_view.was_shown is True
    assert previous_view.was_shown is False

    assert app.error_fallback_view.error_message == "Test error"


@pytest.mark.parametrize("new_state", list(application.state_machine.ViewState))
def test_show_view(app_context, new_state):
    app, root, client = app_context

    previous_state = app.current_state
    previous_view = app.views_by_state[previous_state]

    app._show_view(new_state)

    assert app.current_state is new_state
    assert app.views_by_state[new_state].was_shown is True

    if new_state is not previous_state:
        assert previous_view.was_shown is False


@pytest.mark.parametrize(
    ("previous_state", "new_state"),
    [
        (
            application.state_machine.ViewState.LOCATION_SEARCH,
            application.state_machine.ViewState.WELCOME,
        ),
        (
            application.state_machine.ViewState.LOCATION_RESULTS,
            application.state_machine.ViewState.LOCATION_SEARCH,
        ),
        (
            application.state_machine.ViewState.CURRENT_WEATHER,
            application.state_machine.ViewState.LOCATION_RESULTS,
        ),
    ],
)
def test_handle_back(app_context, previous_state, new_state):
    app, root, client = app_context

    app._show_view(previous_state)

    previous_view = app.views_by_state[previous_state]

    app._handle_back()

    assert app.current_state is new_state
    assert app.views_by_state[new_state].was_shown is True
    assert previous_view.was_shown is False


@pytest.mark.parametrize(
    "return_state",
    [
        application.state_machine.ViewState.LOCATION_SEARCH,
        application.state_machine.ViewState.LOCATION_RESULTS,
    ],
)
def test_return_restores_cached_state(app_context, return_state):
    app, root, client = app_context

    app._show_view(application.state_machine.ViewState.ERROR_FALLBACK)
    app.cached_state = return_state

    app._handle_return()

    assert app.current_state is return_state
    assert app.views_by_state[return_state].was_shown is True
    assert app.error_fallback_view.was_shown is False
    assert app.cached_state is None


def test_return_without_cached_state_shows_welcome(app_context):
    app, root, client = app_context

    app._show_view(application.state_machine.ViewState.ERROR_FALLBACK)
    app.cached_state = None

    app._handle_return()

    assert app.current_state is application.state_machine.ViewState.WELCOME
    assert app.welcome_view.was_shown is True
    assert app.error_fallback_view.was_shown is False
    assert app.cached_state is None
