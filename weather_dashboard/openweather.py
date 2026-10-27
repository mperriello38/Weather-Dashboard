import requests
import math

CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"


class OpenWeatherError(Exception):
    """Base class for failures involving OpenWeather."""


class OpenWeatherTimeoutError(OpenWeatherError):
    """Raised when OpenWeather takes too long to respond."""


class OpenWeatherConnectionError(OpenWeatherError):
    """Raised when OpenWeather cannot be reached."""


class OpenWeatherResponseError(OpenWeatherError):
    """Raised when OpenWeather returns unreadable data."""


class OpenWeatherHTTPError(OpenWeatherError):
    """Raised when OpenWeather returns an unsuccessful HTTP status."""

    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"OpenWeather returned HTTP {status_code}.")


class OpenWeatherClient:
    def __init__(self, api_key, units="imperial", timeout=10):
        if not isinstance(api_key, str):
            raise TypeError("API key must be a string.")

        if not api_key.strip():
            raise ValueError("API key cannot be empty.")

        self.api_key = api_key

        if not isinstance(units, str):
            raise TypeError("Units must be string type.")

        if units not in {"imperial", "standard", "metric"}:
            raise ValueError(
                "Unknown unit type, must be imperial, standard, or metric."
            )

        self.units = units

        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("Timeout must be a number.")

        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Timeout must be a positive finite number.")

        self.timeout = timeout

    def _decode_response(self, response):
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as error:
            raise OpenWeatherResponseError(
                "OpenWeather returned unreadable JSON."
            ) from error

    def get_current_weather(self, latitude, longitude):
        if isinstance(latitude, bool) or not isinstance(latitude, (int, float)):
            raise TypeError("Latitude must be a number.")

        if not math.isfinite(latitude) or not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90.")

        if isinstance(longitude, bool) or not isinstance(longitude, (int, float)):
            raise TypeError("Longitude must be a number.")

        if not math.isfinite(longitude) or not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180.")

        weather_params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": self.units,
        }

        try:
            response = requests.get(
                CURRENT_WEATHER_URL, params=weather_params, timeout=self.timeout
            )
            response.raise_for_status()

        except requests.Timeout as error:
            raise OpenWeatherTimeoutError("The weather request timed out.") from error

        except requests.HTTPError as error:
            raise OpenWeatherHTTPError(response.status_code) from error

        except requests.ConnectionError as error:
            raise OpenWeatherConnectionError(
                "Could not connect to OpenWeather."
            ) from error

        except requests.RequestException as error:
            raise OpenWeatherError("An unexpected request failure occurred.") from error

        return self._decode_response(response)

    def search_locations(self, query, limit=5):
        if not isinstance(query, str):
            raise TypeError("Search query must be string type.")

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("Search result limit must be an integer.")

        if not 1 <= limit <= 5:
            raise ValueError("Search result limit must be between 1 and 5.")

        normalized_query = ",".join(component.strip() for component in query.split(","))
        geocoding_params = {
            "q": normalized_query,
            "appid": self.api_key,
            "limit": limit,
        }

        try:
            response = requests.get(
                GEOCODING_URL, params=geocoding_params, timeout=self.timeout
            )
            response.raise_for_status()

        except requests.Timeout as error:
            raise OpenWeatherTimeoutError("The geocode request timed out.") from error

        except requests.HTTPError as error:
            raise OpenWeatherHTTPError(response.status_code) from error

        except requests.ConnectionError as error:
            raise OpenWeatherConnectionError(
                "Could not connect to OpenWeather."
            ) from error

        except requests.RequestException as error:
            raise OpenWeatherError("An unexpected request failure occured.") from error

        return self._decode_response(response)
