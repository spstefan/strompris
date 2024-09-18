#!/usr/bin/env python3
"""
Fetch data from https://www.hvakosterstrommen.no/strompris-api
and visualize it.

Assignment 5
"""

import datetime

import altair as alt
import pandas as pd
import requests
import requests_cache

# install an HTTP request cache
# to avoid unnecessary repeat requests for the same data
# this will create the file http_cache.sqlite
requests_cache.install_cache()


def fetch_day_prices(date: datetime.date = None, location: str = "NO1") -> pd.DataFrame:
    """Fetch one day of data for one location from hvakosterstrommen.no API

    Args: 
        date (datetime.date): The date to fetch prices for from the API.
        location (str): Location code for the area to fetch the prices for from the API. 
                        Mapping of codes to area can be found at: https://www.hvakosterstrommen.no/strompris-api

    Returns:
        pd.DataFrame: A dataframe containing the hourly price of electricity in different currencies.

    Raises:
        AssertionError: If 'date' is something other than a datetime.date object or None type.
        AssertionError: If 'date' is a date before October 1st 2023. 
        HTTPError: If the GET request to the API fails.
    """
    if date is None:
        date = datetime.date.today() 

    assert isinstance(date, datetime.date), f"Expected {date} to be a {type(datetime.date)} object, but received something else"
    assert date >= datetime.date(2023, 10, 1), f"Expected {date} to be a day after October 1st 2023"

    # Ensures double digits as required per API
    day = date.strftime("%d")
    month = date.strftime("%m")

    # Fetch data from API
    url = f"https://www.hvakosterstrommen.no/api/v1/prices/{date.year}/{month}-{day}_{location}.json"
    r = requests.get(url)
    r.raise_for_status() # Raises HTTP error if status code is something other than 2XX
    data = r.json()

    df = pd.DataFrame.from_dict(data)  # Convert to a dataframe
    df["NOK_per_kWh"]= df["NOK_per_kWh"].astype(float) # Convert column values to float datatype

    # Convert time columns to datetime types, with regards to daylight savings
    df["time_start"] = pd.to_datetime(df["time_start"], utc=True).dt.tz_convert("Europe/Oslo")
    df["time_end"] = pd.to_datetime(df["time_end"], utc=True).dt.tz_convert("Europe/Oslo")

    return df


# LOCATION_CODES maps codes ("NO1") to names ("Oslo")
LOCATION_CODES = {"NO1" : "Oslo",
                  "NO2" : "Kristiansand",
                  "NO3" : "Trondheim",
                  "NO4" : "Tromsø",
                  "NO5" : "Bergen"}


def fetch_prices(
    end_date: datetime.date = None,
    days: int = 7,
    locations: list[str] = tuple(LOCATION_CODES.keys()),
) -> pd.DataFrame:
    """Fetch prices for multiple days and locations into a single DataFrame

    args: 
        end_date (datetime.date): The end date from which to start fetching prices for.
            If None, defaults to today's date. 
        days (int): Number of days to fetch prices for.
            Defaults to 7 days.
        locations (list[str]): A list of location codes for which to fetch prices for. 
            Defaults to tuple of all keys from LOCATION_CODES dictionary. 
    
    Returns:
        pd.DataFrame: A DataFrame containing the hourly price of electricity for a duration of days and 
            different locations, in different currencies. 
    """

    if end_date is None:
        end_date = datetime.date.today()

    dataframes = []

    for location in locations:
        for i in range(days):
            # Starts from end_date and works backwards 'days' times. 
            day_to_fetch = end_date - datetime.timedelta(days=i)

            # Price for given day, in given location:
            day_price = fetch_day_prices(day_to_fetch, location) 

            # Add location and code as column to the dataframe
            day_price["location_code"] = location
            day_price["location"] = LOCATION_CODES[location]

            dataframes.append(day_price)

    df = pd.concat(dataframes)

    return df


def plot_prices(df: pd.DataFrame) -> alt.Chart:
    """Plot energy prices over time

    The x-axis represents time_start.
    The y-axis represents hourly KiloWatt price in NOK.
    Each location is represented with a different colored line.

    args:
        df (pd.DataFrame): A dataframe containing the data to be displayed as a chart

    Returns: 
        alt.Chart: An Altair Chart object of the plot prices over time for a number of locations. 

    Note: I'm having issues with Altair Viewer, won't be able to test this function until later
        when it's up on the webserver
    """
    
    chart = alt.Chart(df).mark_line().encode(
        x='time_start:T',
        y='NOK_per_kWh:Q',
        color='location:N'
    )

    return chart


def plot_daily_prices(df: pd.DataFrame) -> alt.Chart:
    """Plot the daily average price

    x-axis should be time_start (day resolution)
    y-axis should be price in NOK

    You may use any mark.

    Make sure to document arguments and return value...
    """
    ...


ACTIVITIES = {
    # activity name: energy cost in kW
    ...
}


def plot_activity_prices(
    df: pd.DataFrame, activity: str = "shower", minutes: float = 10
) -> alt.Chart:
    """
    Plot price for one activity by name,
    given a data frame of prices, and its duration in minutes.

    Make sure to document arguments and return value...
    """
    raise NotImplementedError("Remove me when you implemnt this optional task")

    ...


def main():
    """Allow running this module as a script for testing."""
    df = fetch_prices()
    chart = plot_prices(df)
    # showing the chart without requiring jupyter notebook or vs code for example
    # requires altair viewer: `pip install altair_viewer`
    chart.show()
    # Note: Didn't work for me, might work for you. 


if __name__ == "__main__":
    main()
