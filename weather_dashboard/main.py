import os
import tkinter as tk

from dotenv import load_dotenv

from .application import WeatherApp
from .openweather import OpenWeatherClient


def main():
    load_dotenv()

    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        raise SystemExit("OPENWEATHER_API_KEY is missing from .env")

    root = tk.Tk()
    weather_client = OpenWeatherClient(API_KEY)
    app = WeatherApp(root, weather_client)

    root.mainloop()


if __name__ == "__main__":
    main()
