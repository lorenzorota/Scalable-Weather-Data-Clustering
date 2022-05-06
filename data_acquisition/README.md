# Data Acquisition Tool

## Scope

This tool handles the data acquisition of live weather data across cities anywhere in the world. The source consists of a range of services provided by <https://www.wunderground.com>, of which the ones used in this project are:

* Location Service Querying for retrieving Personal Weather Station (PWS) IDs
* Real-time observations from PWS endpoints.

The acquired and processed data is then published onto separate channels in the Pub/Sub messaging service provided by <https://www.pubnub.com>, used for creating dependable data streams and data storage for each city.

## Overview

This folder consists of the following python scripts

1. `push_weather_data.py` : The tool responsible for acquiring, processing and publishing the data.

2. `fetch_data.py` : A simple tool for retrieving historic data for a particular city over a given timeframe.

3. `clear_history.py` : A tool for clearing all historic data of all provided cities from the pubnub service.

## Instructions

1. To run the data acquisition tool, make sure you have a weather API key from <https://www.wunderground.com> and a publish and subscribe key from <https://www.pubnub.com>.

2. (Recommended) Create virtual python environment.

    ```bash
    virtualenv env
    ```

3. Install pip requirements.

    ```bash
    pip install -r requirements.txt
    ```

4. Store API keys as environment variables.

    ```bash
    export WEATHER_API_KEY = <INSERT_KEY>
    export PBCONFIG_PUBLISH_KEY = <INSERT_KEY>
    export PBCONFIG_SUBSCRIBE_KEY = <INSERT_KEY>
    ```

5. Populate `cities.txt` (an example is provided).

6. (Optional) when running the data acquisition and publishing tool with the `-R` option, make sure you create a `cookies.txt` file containing the cookies needed for authenticating over <https://www.wunderground.com>.

7. Serve the data acquisition and publishing tool.

    ```bash
    python push_weather_data.py
    ```

    > **_NOTE:_**  To see information on options and arguments, run:
    >
    > ```bash
    > python push_weather_data.py -h
    > ```

8. (Optional) Fetch historical data from a city.

    ```bash
    python fetch_data.py
    ```

    > **_NOTE:_**  The begin and end date follow the ISO-8601 format: e.g. `2021-12-31T00:00:01`
