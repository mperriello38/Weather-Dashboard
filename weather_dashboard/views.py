import tkinter as tk
from tkinter import ttk


# The following are subclasses which inheret from ttk.Frame
# i.e. they create new frame subclasses which are used for each view in desktop mode
class WelcomeView(ttk.Frame):
    def __init__(self, parent, on_begin, on_quit):
        super().__init__(parent, padding=10)

        ttk.Label(self, text="Weather Dashboard V 0.2").grid(
            column=0, row=0, columnspan=2
        )

        ttk.Button(self, text="Click to begin", command=on_begin).grid(column=0, row=1)

        ttk.Button(self, text="Quit", command=on_quit).grid(column=0, row=5)


class LocationSearchView(ttk.Frame):
    def __init__(self, parent, on_search, on_back, on_quit):
        super().__init__(parent, padding=10)

        self._on_search = on_search

        ttk.Label(
            self, text="City, State code, Country (state and country optional):"
        ).grid(column=0, row=0)

        self.location_entry = ttk.Entry(self, width=30)
        self.location_entry.grid(column=1, row=0)

        ttk.Button(self, text="Back", command=on_back).grid(column=0, row=4)

        ttk.Button(self, text="Quit", command=on_quit).grid(column=0, row=5)

        ttk.Button(self, text="Search", command=self._submit_search).grid(
            column=2, row=0
        )

    def _submit_search(self):
        location_query = self.location_entry.get().strip()
        self._on_search(location_query)


class LocationResultsView(ttk.Frame):
    def __init__(self, parent, on_select, on_back, on_quit):
        super().__init__(parent, padding=10)

        self._on_select = on_select

        ttk.Label(self, text="Search results:").grid(column=0, row=0)

        self.results_combobox = ttk.Combobox(self, state="readonly")
        self.results_combobox.grid(column=1, row=0)
        self.results_combobox.bind("<<ComboboxSelected>>", self._selection_changed)

        ttk.Button(self, text="Back", command=on_back).grid(column=0, row=4)

        ttk.Button(self, text="Quit", command=on_quit).grid(column=0, row=5)

    def set_results(self, location_labels):
        self.results_combobox.configure(values=location_labels)

        if location_labels:
            self.results_combobox.current(0)
        else:
            self.results_combobox.set("")

    def _selection_changed(self, _event):
        selected_index = self.results_combobox.current()

        if selected_index != -1:
            self._on_select(selected_index)


class CurrentWeatherView(ttk.Frame):
    def __init__(self, parent, on_back, on_quit, on_start_monitor, on_stop_monitor):
        super().__init__(parent, padding=10)

        self.start_monitor = on_start_monitor
        self.stop_monitor = on_stop_monitor

        self.weather_text_var = tk.StringVar(master=self, value="No location selected.")

        ttk.Label(self, textvariable=self.weather_text_var, justify="center").grid(
            column=0, row=0
        )

        ttk.Button(self, text="Back", command=on_back).grid(column=0, row=4)

        ttk.Button(self, text="Quit", command=on_quit).grid(column=0, row=5)

        self.monitor_button = ttk.Button(
            self, text="Start monitor", command=self.start_monitor
        )
        self.monitor_button.grid(column=1, row=4)

    def set_weather(self, weather_summary):
        self.weather_text_var.set(weather_summary)

    def set_monitor_button(self, is_monitoring):
        if not is_monitoring:
            self.monitor_button.configure(text="Start monitor")
            self.monitor_button.configure(command=self.start_monitor)
        else:
            self.monitor_button.configure(text="Stop monitor")
            self.monitor_button.configure(command=self.stop_monitor)


class ErrorFallbackView(ttk.Frame):
    def __init__(self, parent, on_return, on_quit):
        super().__init__(parent, padding=10)

        self.error_text_var = tk.StringVar(
            master=self, value="An unknown error occurred:"
        )

        ttk.Label(self, textvariable=self.error_text_var, justify="center").grid(
            column=0, row=0
        )

        ttk.Button(self, text="Return", command=on_return).grid(column=0, row=4)

        ttk.Button(self, text="Quit", command=on_quit).grid(column=0, row=5)

    def set_error_message(self, error_message):
        self.error_text_var.set(error_message)
