"""Module"""
# pylint: disable=unused-import, missing-function-docstring

from typing import TypeVar, Optional, Tuple, Dict, List, Any, Iterable

import rcm.lib

import re

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd


tickers_ref_data: pd.DataFrame = pd.read_csv(
    r"data/tickers.csv"
).set_index("Ticker")


def get_timeseries(ticker: str) -> pd.DataFrame:
    import os

    path: str = f"data/cache/{ticker}.csv"
    if os.path.exists(path):
        print(f"INFO: Reading {path}")
        result = pd.read_csv(
            path,
            parse_dates=["Date"],
        ).set_index("Date")
    else:
        print(f"INFO: {path} does not exist.")
        result = rcm.lib.rcm_download_bloomberg_ticker(ticker + " Index").set_index(
            "Date"
        )
        result.to_csv(path)
    return result


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=dcc.Dropdown(
                        id="product-dropdown",
                        options=[
                            {
                                "label": t.Product  # type: ignore[attr-defined]
                                + (
                                    (f" ({t.Underlying}A Comdty)")  # type: ignore[attr-defined]
                                    if type(t.Underlying) == str  # type: ignore[attr-defined]
                                    else ""
                                ),
                                "value": t.Product,  # type: ignore[attr-defined]
                            }
                            for t in tickers_ref_data[["Product", "Underlying"]]
                            .drop_duplicates()
                            .itertuples(index=False)
                        ],
                    )
                )
            ],
            className="py-1",
        ),
        html.Div(
            id="ticker-graphs",
            children=[rcm.lib.as_html_table([("test", "hello")])],
        ),
    ],
    fluid=True,
)


def main() -> None:
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
