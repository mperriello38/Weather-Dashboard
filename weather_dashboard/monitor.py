import concurrent.futures

from . import openweather

class Monitor:
    def __init__(self, client, location, root, on_weather, on_error):
        self.client = client
        self.location = location
        self.root = root
        self.on_weather = on_weather
        self.on_error = on_error

        self.is_monitoring = False

        self.refresh_future = None
        self.refresh_timer_id = None

        self.check_timer_id = None

        self.refresh_interval = 900_000

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def start(self):
        if self.is_monitoring:
            return
        else:
            self.is_monitoring = True

        self.refresh_future = self.executor.submit(
            self.client.get_current_weather, self.location["lat"], self.location["lon"]
        )
        self._check_refresh_result()

    def stop(self):
        if not self.is_monitoring:
            return
        else:
            self.is_monitoring = False

        if self.refresh_timer_id != None:
            self.root.after_cancel(self.refresh_timer_id)

        if self.check_timer_id != None:
            self.root.after_cancel(self.check_timer_id)

    def close(self):
        self.is_monitoring = False

        self.executor.shutdown(wait=False, cancel_futures=True)

    def _refresh_weather(self):
        self.refresh_future = self.executor.submit(
            self.client.get_current_weather, self.location["lat"], self.location["lon"]
        )
        self._check_refresh_result()

    def _check_refresh_result(self):
        if not self.is_monitoring:
            return
        
        if not self.refresh_future.done():
            self.check_timer_id = self.root.after(100, self._check_refresh_result)
            return

        try:
            self.last_response = self.refresh_future.result()

        except concurrent.futures.CancelledError:
            return

        except openweather.OpenWeatherError as error:
            self.on_error(error)

        else:
            self.on_weather(self.last_response)

        if self.is_monitoring:
            self.refresh_timer_id = self.root.after(
                self.refresh_interval, self._refresh_weather
            )

    def _update_monitor(self):
        if self.is_monitoring:
            self.on_weather(self.last_response)

        self.refresh_timer_id = self.root.after(
            self.refresh_interval, self._refresh_weather
        )
