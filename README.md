# Weather Dashboard

A small weather monitoring program developed and tested with Python 3.11.5 with a tkinter UI and OpenWeather API integration.

The program is controlled by an instance of the WeatherApp class in application.py. The WeatherApp is passed a tkinter root (and a client containing the API key and associated call and response methods). The various functionalities of the program
are primarily divided into "views" which are classes that inherit from tkinter.ttk.Frame. The views.py is responsible for rendering the interface and forwarding user actions. This lets the WeatherApp simply pass the various functions to be called by buttons already attached to the tkinter frames. Currently the program supports
location lookup using the OpenWeather GeoCode API. Once a location is selected, monitor mode can be enabled which will automatically call the OpenWeather API and updates the weather with a 15 minute polling interval.

## Current Issues
The monitor system has several known issues and will be fixed soon. For now, use manual weather lookup and avoid clicking Start monitor.

## Planned Features

Ultimately the project will be integrated with NZXT's monitoring program to allow the weather data to be displayed on connected devices. In the near-term a code refactor is planned as well as the addition of more unit tests and the first
integration tests.

## API-key Setup

1. Create an [OpenWeather account](https://home.openweathermap.org/users/sign_up), then copy your key from the [API keys page](https://home.openweathermap.org/api_keys).

2. If you do not already have a `.env` file, copy the example from the project root in PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Open `.env` and replace the placeholder with your own key:

   ```dotenv
   OPENWEATHER_API_KEY=your_api_key_here
   ```

The application loads `.env` automatically at startup. Keep your real API key private: `.env` is excluded by `.gitignore`, and `.env.example` should contain only a placeholder.

## Running the Program:
From the project root in PowerShell:

To install the required libraries:
```powershell
python -m pip install -r requirements-dev.txt
```

To run the program:
```powershell
python -m weather_dashboard.main
```

To run the development tests:
```powershell
python -m pytest
```
