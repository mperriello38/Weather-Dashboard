from enum import Enum


class ViewState(Enum):
    WELCOME = 1
    LOCATION_SEARCH = 2
    LOCATION_RESULTS = 3
    CURRENT_WEATHER = 4
    ERROR_FALLBACK = 5


class NavigationEvent(Enum):
    BEGIN = 1
    SEARCH_SUBMITTED = 2
    LOCATION_SELECTED = 3
    BACK = 4


# Error states and events are handled in application.py. If an error state or event is passed
# to next_state, SOMETHING IS WRONG!
def next_state(current_state, event):
    if not isinstance(current_state, ViewState):
        raise TypeError("Current state must be a member of ViewState enum class.")

    if not isinstance(event, NavigationEvent):
        raise TypeError("Event must be a member of NavigationEvent enum class.")

    if current_state is ViewState.WELCOME and event is NavigationEvent.BEGIN:
        return ViewState.LOCATION_SEARCH

    if current_state is ViewState.LOCATION_SEARCH:
        if event is NavigationEvent.SEARCH_SUBMITTED:
            return ViewState.LOCATION_RESULTS
        elif event is NavigationEvent.BACK:
            return ViewState.WELCOME

    if current_state is ViewState.LOCATION_RESULTS:
        if event is NavigationEvent.LOCATION_SELECTED:
            return ViewState.CURRENT_WEATHER
        elif event is NavigationEvent.BACK:
            return ViewState.LOCATION_SEARCH

    if current_state is ViewState.CURRENT_WEATHER:
        if event is NavigationEvent.BACK:
            return ViewState.LOCATION_RESULTS

    return current_state
