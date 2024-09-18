"""
strompris fastapi app entrypoint
"""
import datetime
import os
from typing import List, Optional

import altair as alt
from fastapi import FastAPI, Query, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import uvicorn
from strompris import (
    ACTIVITIES,
    LOCATION_CODES,
    fetch_day_prices,
    fetch_prices,
    plot_activity_prices,
    plot_daily_prices,
    plot_prices,
)

# Setup for FastAPI and Jinja template
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mounts docs directory as static files at `/help`
app.mount("/help", StaticFiles(directory="./docs/_build/html", html=True), name="sphinx_docs")


# `GET /` should render the `strompris.html` template
# with inputs:
# - request
# - location_codes: location code dict
# - today: current date
@app.get("/")
def get_strompris(request: Request, location_codes: dict = None, today: datetime.date = None):
       
       # Setting defaults if None is given
       if today is None:
            today = datetime.date.today()

       if location_codes is None:
            location_codes = LOCATION_CODES
   
       # Render template with inputs
       return templates.TemplateResponse(
        "strompris.html",
        {
            "request": request,
            "location_codes": location_codes,
            "today": today
        },
    )


# GET /plot_prices.json should take inputs:
# - locations (list from Query)
# - end (date)
# - days (int, default=7)
# all inputs should be optional
# return should be a vega-lite JSON chart (alt.Chart.to_dict())
# produced by `plot_prices`
@app.get("/plot_prices.json")
def get_plot_prices(request: Request, end: datetime.date = None, days: int = None, locations: List[str] = Query(None)):
    
    # Setting defaults if None is given
    if end is None:
        end = datetime.date.today()

    if days is None:
        days = 7

    if locations is None:
          locations = list(LOCATION_CODES.keys())

    # Creating the dataframe and corresponding chart
    df = fetch_prices(end, days, locations)
    chart = plot_prices(df)

    return chart.to_dict()

# NOT IMPLEMENTED
    # Task 5.6 (bonus):
    # `GET /activity` should render the `activity.html` template
    # activity.html template must be adapted from `strompris.html`
    # with inputs:
    # - request
    # - location_codes: location code dict
    # - activities: activity energy dict
    # - today: current date

# NOT IMPLEMENTED
    # Task 5.6:
    # `GET /plot_activity.json` should return vega-lite chart JSON (alt.Chart.to_dict())
    # from `plot_activity_prices`
    # with inputs:
    # - location (single, default=NO1)
    # - activity (str, default=shower)
    # - minutes (int, default=10)


def main():
    """Launches the application on port 5000 with uvicorn"""
    # use uvicorn to launch your application on port 5000
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)

if __name__ == "__main__":
    main()
