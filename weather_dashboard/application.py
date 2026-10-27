from . import formatters
from . import monitor
from . import state_machine
from . import views

from . import openweather


# Main class for handling desktop mode
# Each frame is mounted to one root, and each ui screen is attatched to a corresponding frame.
# The views_by_state dictionary has keys according to state_machine.ViewState and values of the corresponding view.
class WeatherApp:
    def __init__(self, root, weather_client):
        self.root = root
        self.weather_client = weather_client

        self.current_state = None
        self.cached_state = None
        self.location_results = []
        self.selected_location = None

        self.views_by_state = {}

        self.monitor_controller = None

        self._build_views()
        self._show_view(state_machine.ViewState.WELCOME)

    def _show_view(self, new_state):
        if self.current_state is not None:
            self.views_by_state[self.current_state].grid_remove()

        self.views_by_state[new_state].grid()
        self.current_state = new_state

    def _handle_quit(self):
        self.root.destroy()

    def _handle_back(self):
        next_state = state_machine.next_state(
            self.current_state, state_machine.NavigationEvent.BACK
        )
        self._show_view(next_state)

    def _handle_begin(self):
        next_state = state_machine.next_state(
            self.current_state, state_machine.NavigationEvent.BEGIN
        )
        self._show_view(next_state)

    def _handle_return(self):
        if self.cached_state is not None:
            self._show_view(self.cached_state)
        else:
            self._show_view(state_machine.ViewState.WELCOME)

        self.cached_state = None

    def _show_error(self, error):
        self.error_fallback_view.set_error_message(str(error))
        self._show_view(state_machine.ViewState.ERROR_FALLBACK)

    def _handle_search(self, location_query):
        try:
            self.location_results = self.weather_client.search_locations(location_query)

        except ValueError as error:
            self.cached_state = state_machine.ViewState.LOCATION_SEARCH
            self._show_error(error)
            return

        except openweather.OpenWeatherTimeoutError as error:
            self.cached_state = state_machine.ViewState.LOCATION_SEARCH
            self._show_error(error)
            return

        except openweather.OpenWeatherHTTPError as error:
            self.cached_state = state_machine.ViewState.WELCOME
            self._show_error(error)
            return

        except openweather.OpenWeatherConnectionError as error:
            self.cached_state = state_machine.ViewState.LOCATION_SEARCH
            self._show_error(error)
            return

        except openweather.OpenWeatherError as error:
            self.cached_state = state_machine.ViewState.WELCOME
            self._show_error(error)
            return

        location_labels = formatters.format_location_options(self.location_results)

        self.location_results_view.set_results(location_labels)

        next_state = state_machine.next_state(
            self.current_state, state_machine.NavigationEvent.SEARCH_SUBMITTED
        )
        self._show_view(next_state)

    def _handle_location_selected(self, selected_index):
        self.selected_location = self.location_results[selected_index]

        try:
            weather_data = self.weather_client.get_current_weather(
                self.selected_location["lat"], self.selected_location["lon"]
            )

        except ValueError as error:
            self.cached_state = state_machine.ViewState.LOCATION_RESULTS
            self._show_error(error)
            return

        except openweather.OpenWeatherTimeoutError as error:
            self.cached_state = state_machine.ViewState.LOCATION_RESULTS
            self._show_error(error)
            return

        except openweather.OpenWeatherHTTPError as error:
            self.cached_state = state_machine.ViewState.WELCOME
            self._show_error(error)
            return

        except openweather.OpenWeatherConnectionError as error:
            self.cached_state = state_machine.ViewState.LOCATION_RESULTS
            self._show_error(error)
            return

        except openweather.OpenWeatherError as error:
            self.cached_state = state_machine.ViewState.WELCOME
            self._show_error(error)
            return

        weather_summary = formatters.format_current_weather(
            self.selected_location, weather_data, self.weather_client.units
        )

        self.current_weather_view.set_weather(weather_summary)

        if self.monitor_controller is not None and self.monitor_controller.is_monitoring:
            self.monitor_controller.stop()
            self._handle_monitor_start()

        next_state = state_machine.next_state(
            self.current_state, state_machine.NavigationEvent.LOCATION_SELECTED
        )
        self._show_view(next_state)

    def _handle_weather_updated(self, weather_data):
        weather_summary = formatters.format_current_weather(
            self.selected_location, weather_data, self.weather_client.units
        )

        self.current_weather_view.set_weather(weather_summary)

    def _handle_monitor_error(self, error):
        print(f"Weather refresh failed: {error}")

    def _handle_monitor_start(self):
        self.monitor_controller = monitor.Monitor(
            self.weather_client,
            self.selected_location,
            self.root,
            self._handle_weather_updated,
            self._handle_monitor_error,
        )

        self.monitor_controller.start()

        self.current_weather_view.set_monitor_button(
            self.monitor_controller.is_monitoring
        )

    def _handle_monitor_stop(self):
        self.monitor_controller.stop()

        self.current_weather_view.set_monitor_button(
            self.monitor_controller.is_monitoring
        )

    def _build_views(self):
        self.welcome_view = views.WelcomeView(
            self.root, self._handle_begin, self._handle_quit
        )

        self.location_search_view = views.LocationSearchView(
            self.root, self._handle_search, self._handle_back, self._handle_quit
        )

        self.location_results_view = views.LocationResultsView(
            self.root,
            self._handle_location_selected,
            self._handle_back,
            self._handle_quit,
        )

        self.current_weather_view = views.CurrentWeatherView(
            self.root,
            self._handle_back,
            self._handle_quit,
            self._handle_monitor_start,
            self._handle_monitor_stop,
        )

        self.error_fallback_view = views.ErrorFallbackView(
            self.root, self._handle_return, self._handle_quit
        )

        self.views_by_state = {
            state_machine.ViewState.WELCOME: self.welcome_view,
            state_machine.ViewState.LOCATION_SEARCH: self.location_search_view,
            state_machine.ViewState.LOCATION_RESULTS: self.location_results_view,
            state_machine.ViewState.CURRENT_WEATHER: self.current_weather_view,
            state_machine.ViewState.ERROR_FALLBACK: self.error_fallback_view,
        }
