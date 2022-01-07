"""Module"""
# pylint: disable=unused-import, missing-function-docstring

from typing import TypeVar, Optional, Tuple, Any, Iterable, Callable

import itertools
import time

from dash import html
import dash_bootstrap_components as dbc
import pandas as pd


def rcm_download_bloomberg_ticker(ticker: str, field: str) -> pd.DataFrame:
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
        result = pd.read_csv(
            buf, parse_dates=["Date"], dtype=str, usecols=["Date", field]
        )  # result is left as string to avoid parsing numbers at this stage
    result = result[result[field].map(lambda x: type(x) == str)]  # strip NaN
    result[field] = pd.to_numeric(result[field])
    print(
        f'INFO: Downloaded ticker "{ticker}" in '
        f"{(time.perf_counter_ns() - start_time) / 1000000}ms"
    )
    return result


################################################################################

Index = TypeVar("Index")


def get_nearest_index(timeseries: pd.DataFrame, i: Index) -> Optional[Index]:
    try:
        return timeseries.index[timeseries.index.get_loc(i, method="nearest")]  # type: ignore[attr-defined, return-value]
    except KeyError:
        return None


def index_from_product(i1: pd.MultiIndex, i2: pd.MultiIndex) -> pd.MultiIndex:
    """Outer product of indices. Relative ordering is maintained."""
    new_idx_frame = i1.to_frame().merge(i2.to_frame(), how="cross")  # type: ignore[call-overload]
    return pd.MultiIndex.from_frame(new_idx_frame)


def inner_expand(df: pd.DataFrame, f_index: pd.MultiIndex, f: Callable) -> pd.DataFrame:
    def series_inner_expand(
        df: pd.Series, f_index: pd.MultiIndex, f: Callable
    ) -> pd.Series:
        new_index = index_from_product(df.index, f_index)  # type: ignore[arg-type]
        result = pd.Series(  # type: ignore[call-arg]
            itertools.chain.from_iterable(f(df[c]) for c in df.index),  # type: ignore[arg-type]
            index=new_index,
            dtype=object,
        )
        return result

    return df.apply(  # type: ignore[return-value]
        lambda row: series_inner_expand(row, f_index, f),
        axis=1,
    )

################################################################################

def to_string_truncate_if_float(x: Any, digits: int) -> str:
    if type(x) == float:
        return ("%." + str(digits) + "f") % x
    return str(x)

def as_html_table(  # type: ignore[no-untyped-def]
    ls: Iterable[Tuple], colHeaders: bool = True, rowHeaders: bool = True
):
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
