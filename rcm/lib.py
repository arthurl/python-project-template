"""Module"""
# pylint: disable=unused-import, missing-function-docstring

from typing import TypeVar, Optional, Tuple, Any, Iterable

import time

from dash import html
import dash_bootstrap_components as dbc
import pandas as pd


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
        result = pd.read_csv(buf, parse_dates=["Date"])
    print(
        f'INFO: Downloaded ticker "{ticker}" in '
        f"{(time.perf_counter_ns() - start_time) / 1000000}ms"
    )
    return result[result["Message"] != "No response for date"][["Date", "Last"]]


Index = TypeVar("Index")


def get_nearest_index(timeseries: pd.DataFrame, i: Index) -> Optional[Index]:
    try:
        return timeseries.index[timeseries.index.get_loc(i, method="nearest")]  # type: ignore[attr-defined, return-value]
    except KeyError:
        return None


################################################################################


def as_html_table(
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
