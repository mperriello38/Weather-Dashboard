def format_location_options(locations):
    location_labels = []

    for location in locations:
        location_labels.append(
            f"{location['name']}, "
            f"{location.get('state', 'No state/region')}, "
            f"{location['country']}"
        )

    return location_labels


def format_current_weather(location, weather_data, units):
    if not isinstance(units, str):
        raise TypeError("Units must be a string.")

    if not units.strip():
        raise ValueError("Units cannot be empty.")

    if units not in {"imperial", "metric", "standard"}:
        raise ValueError("Units must be imperial, metric, or standard.")

    if units == "imperial":
        temp_unit = "°F"
    elif units == "metric":
        temp_unit = "°C"
    elif units == "standard":
        temp_unit = "K"

    region = location.get("state", "No state/region")
    measurements = weather_data["main"]
    description = weather_data["weather"][0]["description"].title()

    return (
        f"Weather for {location['name']}, "
        f"{region}, {location['country']}\n"
        f"{description}\n"
        f"Temperature: {measurements['temp']:.1f}{temp_unit}\n"
        f"Feels like: {measurements['feels_like']:.1f}{temp_unit}\n"
        f"Humidity: {measurements['humidity']}%"
    )
