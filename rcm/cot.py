"""Module"""
# pylint: disable=unused-import, missing-function-docstring

import rcm.lib

from typing import Dict, List, Any

import time

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd


################################################################################


tickers_ref_data: pd.DataFrame = pd.read_csv(r"data/tickers.csv").set_index("Ticker")


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


def mk_card(ticker: str):  # type: ignore[no-untyped-def]
    ticker_ref_data = tickers_ref_data.loc[ticker]
    ts = get_timeseries(ticker)

    metric = str.title(str(ticker_ref_data["Metric"]))
    df_graph = dcc.Graph(
        figure=px.scatter(
            ts,
            x=ts.index,
            y="Last",
            labels={
                (ts.index.name): str.title(ts.index.name),  # type: ignore[attr-defined]
                "Last": metric,
            },
        ).update_layout(
            margin={"t": 0, "l": 0, "r": 0, "b": 0}
        ),  # remove top margins
    )

    last_dt = ts.index.max()
    last_wk_dt = rcm.lib.get_nearest_index(ts, last_dt - pd.tseries.offsets.Day(7))  # type: ignore[attr-defined]
    last_yr_dt = rcm.lib.get_nearest_index(ts, last_dt - pd.tseries.offsets.Day(365))  # type: ignore[attr-defined]

    last_week_year_table = rcm.lib.as_html_table(
        [
            (None, "Date", str.title(metric)),
            (
                "Last",
                last_dt.date(),  # type: ignore[attr-defined]
                ts.loc[last_dt].values[0],  # type: ignore[call-overload]
            ),
            (
                "~Week",
                last_wk_dt.date(),  # type: ignore[union-attr]
                ts.loc[last_wk_dt].values[0] if last_wk_dt else "<not available>",
            ),
            (
                "~Year",
                last_yr_dt.date(),  # type: ignore[union-attr]
                ts.loc[last_yr_dt].values[0] if last_yr_dt else "<not available>",
            ),
        ]
    )
    details_table = rcm.lib.as_html_table(
        [
            (
                "Product",
                str(ticker_ref_data["Product"]),
            ),
            (
                "Direction",
                str(ticker_ref_data["Direction"]),
            ),
            (
                "Type",
                str(ticker_ref_data["TraderType"]),
            ),
        ]
        + [
            ("Activity", str(act))
            for act in [ticker_ref_data["Activity"]]
            if type(act) == str  # if value does not exist, pandas returns NaN
        ]
        + [
            (
                "Source",
                str(ticker_ref_data["Source"]),
            ),
        ],
        colHeaders=False,
    )

    return dbc.Card(
        [
            dbc.CardHeader(html.Span(children=ticker, id=ticker + "-card-header")),
            dbc.Tooltip(
                children=str(ticker_ref_data["Description"]),
                target=ticker + "-card-header",
            ),
            dbc.CardBody(
                children=dbc.Container(
                    dbc.Row(
                        children=[
                            dbc.Col(children=df_graph, width=9),
                            dbc.Col(
                                children=[
                                    details_table,
                                    last_week_year_table,
                                ],
                                width=3,
                            ),
                        ]
                    ),
                    fluid=True,
                )
            ),
        ]
    )


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=dcc.Dropdown(
                        id="ticker-dropdown",
                        options=[
                            {
                                "label": tk
                                + " ("
                                + tickers_ref_data.loc[tk, "Description"]
                                + ")",
                                "value": tk,
                            }
                            for tk in tickers_ref_data.index.values  # type: ignore[attr-defined]
                        ],
                    )
                )
            ],
            className="py-1",
        ),
        html.Div(
            id="ticker-graphs",
            children=[
                # dbc.Row(
                #     children=[dbc.Col(mk_card("CFFDQMML Index"))],
                #     className="py-1",
                # ),
            ],
        ),
    ],
    fluid=True,
)


Dropdown = List[Dict[str, str]]


@app.callback(
    output=dict(
        dropdown_options=Output("ticker-dropdown", "options"),
        ticker_graphs=Output("ticker-graphs", "children"),
    ),
    inputs=dict(
        ticker=Input("ticker-dropdown", "value"),
        dropdown_options=Input("ticker-dropdown", "options"),
        ticker_graphs=State("ticker-graphs", "children"),
    ),
)
def add_ticker(  # type: ignore[no-untyped-def]
    ticker: str, dropdown_options: Dropdown, ticker_graphs: List[Any]
):  # note: doesn't work with annotated result type..?
    start_time = time.perf_counter_ns()
    if ticker:
        idx = next(
            (i for i, x in enumerate(dropdown_options) if x["value"] == ticker), None
        )
        if idx is None:  # note that 0 is a valid value!
            raise AssertionError("Ticker must exist in dropdown!")
        del dropdown_options[idx]

        ticker_graphs.insert(
            0,
            dbc.Row(
                key=ticker + "-graph-row",
                children=[dbc.Col(mk_card(ticker))],
                className="py-1",
            ),
        )
    print(
        r"INFO: Elasped wall time for add_ticker callback: "
        f"{(time.perf_counter_ns() - start_time) / 1000000}ms"
    )
    return dict(dropdown_options=dropdown_options, ticker_graphs=ticker_graphs)


def main() -> None:
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
