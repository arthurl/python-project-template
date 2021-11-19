"""Module"""
# pylint: disable=unused-import, missing-function-docstring

from typing import TypeVar, Optional, Tuple, Dict, List, Any, Iterable

import time

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd


################################################################################


def asHtmlTable(
    ls: Iterable[Tuple], colHeaders: bool = True, rowHeaders: bool = True
) -> Any:
    it = iter(ls)
    table = []
    if colHeaders:
        try:
            headers = next(it)
            table.append(
                html.Thead(html.Tr([(html.Th(h) if h else html.Th()) for h in headers]))
            )
        except StopIteration:
            pass
    table.append(
        html.Tbody(
            children=[
                html.Tr(
                    [html.Th(r[0]) if rowHeaders else html.Td(r[0])]
                    + [html.Td(x) for x in r[1:]]
                )
                for r in it
                if r
            ]
        )
    )
    return dbc.Table(table)


Index = TypeVar("Index")


def get_nearest_index(timeseries: pd.DataFrame, i: Index) -> Optional[Index]:
    try:
        return timeseries.index[timeseries.index.get_loc(i, method="nearest")]  # type: ignore[attr-defined, return-value]
    except KeyError:
        return None


def rcm_download_bloomberg_ticker(ticker: str) -> pd.DataFrame:
    import urllib
    import io
    import win32com.client  # type: ignore
    import pythoncom  # type: ignore

    url = r"http://quantweb/workflow-coordinator/workflows/run/HistoricSnapperTimeSeries.csv"
    query = {
        "StartDate": "1970-01-01",
        "EndDate": "2199-01-01",
        "SnapFields": "Last",
        "Field": "Price",
        "Tickers": ticker,
    }
    # This code here is to set up NTLM authentication
    h = win32com.client.Dispatch("WinHTTP.WinHTTPRequest.5.1", pythoncom.CoInitialize())
    h.SetAutoLogonPolicy(0)
    print(f'INFO: Downloading ticker "{ticker}"')
    start_time = time.perf_counter_ns()
    h.Open("POST", url + "?" + urllib.parse.urlencode(query), False)  # type: ignore[attr-defined]
    h.Send()
    with io.StringIO(h.responseText) as buf:
        result = pd.read_csv(buf, parse_dates=["Date"]).rename(columns=str.lower)  # type: ignore[arg-type]
    print(
        f'INFO: Downloaded ticker "{ticker}" in '
        f"{(time.perf_counter_ns() - start_time) / 1000000}ms"
    )
    return result[result["message"] != "No response for date"][["date", "last"]]


################################################################################


tickers_ref_data: pd.DataFrame = (
    pd.read_csv(r"c:/src/cotdatafetcher/test_data/tickers.csv")
    .rename(columns=str.lower)  # type: ignore
    .set_index("ticker")
)


def get_timeseries(ticker: str) -> pd.DataFrame:
    import os

    path: str = f"c:/src/python/python-project-template/data/{ticker}.csv"
    if os.path.exists(path):
        print(f"INFO: Reading {path}")
        result = pd.read_csv(
            path,
            parse_dates=["date"],
        ).set_index("date")
    else:
        print(f"INFO: {path} does not exist.")
        result = rcm_download_bloomberg_ticker(ticker).set_index("date")
        result.to_csv(path)
    return result


def f(ticker: str) -> pd.DataFrame:
    result = pd.read_csv(
        f"c:/src/python/python-project-template/data/{ticker}.csv",
        parse_dates=["date"],
    ).set_index("date")
    return result


def mk_card(ticker: str):  # type: ignore[no-untyped-def]
    ticker_ref_data = tickers_ref_data.loc[ticker]
    ts = get_timeseries(ticker)

    metric = str.title(str(ticker_ref_data["metric"]))
    df_graph = dcc.Graph(
        figure=px.scatter(
            ts,
            x=ts.index,
            y="last",
            labels={
                (ts.index.name): str.title(ts.index.name),  # type: ignore[attr-defined]
                "last": metric,
            },
        ).update_layout(
            margin={"t": 0, "l": 0, "r": 0, "b": 0}
        ),  # remove top margins
    )

    last_dt = ts.index.max()
    last_wk_dt = get_nearest_index(ts, last_dt - pd.tseries.offsets.Day(7))  # type: ignore[attr-defined]
    last_yr_dt = get_nearest_index(ts, last_dt - pd.tseries.offsets.Day(365))  # type: ignore[attr-defined]

    last_week_year_table = asHtmlTable(
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
    details_table = asHtmlTable(
        [
            (
                "Product",
                str(ticker_ref_data["cot product"]),
            ),
            (
                "Direction",
                str(ticker_ref_data["direction"]),
            ),
            (
                "Type",
                str(ticker_ref_data["tradertype"]),
            ),
        ]
        + [
            ("Activity", str(act))
            for act in [ticker_ref_data["activity"]]
            if type(act) == str  # if value does not exist, pandas returns NaN
        ]
        + [
            (
                "Source",
                str(ticker_ref_data["cot source"]),
            ),
        ],
        colHeaders=False,
    )

    return dbc.Card(
        [
            dbc.CardHeader(html.Span(children=ticker, id=ticker + "-card-header")),
            dbc.Tooltip(
                children=str(ticker_ref_data["description"]),
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
                                + tickers_ref_data.loc[tk, "description"]
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
