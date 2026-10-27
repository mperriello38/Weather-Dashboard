import pytest

from weather_dashboard import state_machine as sm

state = sm.ViewState
event = sm.NavigationEvent


@pytest.mark.parametrize(
    ("input_state", "event", "expected_output"),
    [
        # Valid transitions
        (state.WELCOME, event.BEGIN, state.LOCATION_SEARCH),
        (state.LOCATION_SEARCH, event.SEARCH_SUBMITTED, state.LOCATION_RESULTS),
        (state.LOCATION_RESULTS, event.LOCATION_SELECTED, state.CURRENT_WEATHER),
        (state.CURRENT_WEATHER, event.BACK, state.LOCATION_RESULTS),
        (state.LOCATION_RESULTS, event.BACK, state.LOCATION_SEARCH),
        (state.LOCATION_SEARCH, event.BACK, state.WELCOME),
        # Invalid transitions
        (state.WELCOME, event.BACK, state.WELCOME),
        (state.WELCOME, event.SEARCH_SUBMITTED, state.WELCOME),
        (state.WELCOME, event.LOCATION_SELECTED, state.WELCOME),
        (state.LOCATION_SEARCH, event.BEGIN, state.LOCATION_SEARCH),
        (state.LOCATION_SEARCH, event.LOCATION_SELECTED, state.LOCATION_SEARCH),
        (state.LOCATION_RESULTS, event.BEGIN, state.LOCATION_RESULTS),
        (state.LOCATION_RESULTS, event.SEARCH_SUBMITTED, state.LOCATION_RESULTS),
        (state.CURRENT_WEATHER, event.BEGIN, state.CURRENT_WEATHER),
        (state.CURRENT_WEATHER, event.SEARCH_SUBMITTED, state.CURRENT_WEATHER),
        (state.CURRENT_WEATHER, event.LOCATION_SELECTED, state.CURRENT_WEATHER),
    ],
)
def test_next_state_returns_expected_state(input_state, event, expected_output):
    assert sm.next_state(input_state, event) is expected_output


@pytest.mark.parametrize(
    ("input_state", "input_event", "expected_error"),
    [
        ("WELCOME", event.BEGIN, TypeError),
        (3, event.BEGIN, TypeError),
        (state.WELCOME, "BEGIN", TypeError),
        (state.WELCOME, 1, TypeError),
    ],
)
def test_next_state_rejects_invalid_inputs(input_state, input_event, expected_error):
    with pytest.raises(expected_error):
        sm.next_state(input_state, input_event)
