"""Module"""
# pylint: disable=unused-import, missing-function-docstring

from typing import Optional, Tuple, Dict, List, Any

import rcm.lib

import functools
import time
import math

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd


def get_timeseries(ticker: str, field: str) -> pd.DataFrame:
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
        result = rcm.lib.rcm_download_bloomberg_ticker(
            ticker + " Index", field
        ).set_index("Date")
        result.to_csv(path)
    return result


def get_history_summary(ticker: Any) -> Tuple:
    default_result = ((None, "--"),) * 4
    if type(ticker) != str:
        return default_result

    ts = get_timeseries(ticker, "Last")
    last_dt = ts.index.max()
    last_wk_dt = rcm.lib.get_nearest_index(ts, last_dt - pd.tseries.offsets.Day(7))  # type: ignore[attr-defined]
    last_4wk_dt = rcm.lib.get_nearest_index(ts, last_dt - pd.tseries.offsets.Day(28))  # type: ignore[attr-defined]
    last_yr_dt = rcm.lib.get_nearest_index(ts, last_dt - pd.tseries.offsets.Day(365))  # type: ignore[attr-defined]
    last_value = ts.loc[last_dt].values[0]  # type: ignore[call-overload]
    result = (
        (last_dt.date(), last_value),  # type: ignore[attr-defined]
        (
            last_wk_dt.date(),  # type: ignore[union-attr]
            (
                (ts.loc[last_wk_dt].values[0] - last_value)
                if last_wk_dt
                else default_result[1]
            ),
        ),
        (
            last_4wk_dt.date(),  # type: ignore[union-attr]
            (
                (ts.loc[last_4wk_dt].values[0] - last_value)
                if last_4wk_dt
                else default_result[2]
            ),
        ),
        (
            last_yr_dt.date(),  # type: ignore[union-attr]
            (
                (ts.loc[last_yr_dt].values[0] - last_value)
                if last_yr_dt
                else default_result[3]
            ),
        ),
    )
    return result


def mk_cftc_disaggregated(ref_df: pd.DataFrame) -> pd.DataFrame:
    ref_df = ref_df[  # type: ignore[operator]
        [
            "Ticker",
            "AssetType",
            "TraderType",
            "Direction",
            "Metric",
        ]
    ].pivot(
        values="Ticker",
        index=["TraderType", "Direction"],
        columns=["AssetType", "Metric"],
    )
    return rcm.lib.inner_expand(
        ref_df,
        pd.MultiIndex.from_arrays(
            [pd.Series(["Last", "Δ1wk", "Δ4wk", "Δ1yr"], name="Time")]  # type: ignore[call-arg]
        ),
        lambda x: (y[1] for y in get_history_summary(x)),
    )


def mk_cftc_legacy(ref_df: pd.DataFrame) -> pd.DataFrame:
    return mk_cftc_disaggregated(ref_df)


def mk_mifid(ref_df: pd.DataFrame) -> pd.DataFrame:
    ref_df = ref_df[  # type: ignore[operator]
        [
            "Ticker",
            "TraderType",
            "Activity",
            "Direction",
            "Metric",
        ]
    ].pivot(
        values="Ticker",
        index=["TraderType", "Direction"],
        columns=["Activity", "Metric"],
    )
    return rcm.lib.inner_expand(
        ref_df,
        pd.MultiIndex.from_arrays(
            [pd.Series(["Last", "Δ1wk", "Δ4wk", "Δ1yr"], name="Time")]  # type: ignore[call-arg]
        ),
        lambda x: (y[1] for y in get_history_summary(x)),
    )


tickers_ref_data: pd.DataFrame = pd.read_csv(
    r"data/tickers.csv"
)


def get_relevant(product: str, regulation: str, report_type: Optional[str]):  # type: ignore[no-untyped-def]
    product_ref = tickers_ref_data[
        (tickers_ref_data["Product"] == product)
        & (tickers_ref_data["Regulation"] == regulation)
    ]
    if report_type:
        product_ref = product_ref[product_ref["ReportType"] == report_type]

    return product_ref


app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://codepen.io/chriddyp/pen/bWLwgP.css",
    ],
)


test_df = tickers_ref_data[
    (tickers_ref_data["Product"] == "US Crude WTI Future")
    & (tickers_ref_data["Regulation"] == "CFTC")
    & (tickers_ref_data["ReportType"] == "All Disaggregated")
    & (tickers_ref_data["Source"] == "New York Mercantile Exchange")
]

app.layout = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    width=7,
                    children=dcc.Dropdown(
                        id="product-selection",
                        options=[
                            {
                                "label": product
                                + " ("
                                + "/".join(
                                    i for i in items["Underlying"] if type(i) == str
                                )
                                + ")",
                                "value": product,
                            }
                            for product, items in tickers_ref_data[  # type: ignore[call-arg]
                                ["Product", "Underlying"]
                            ]
                            .drop_duplicates(ignore_index=True)
                            .groupby("Product")
                        ],
                    ),
                ),
                dbc.Col(
                    width=1,
                    children=dcc.RadioItems(
                        id="regulation-selection",
                        labelStyle={"display": "block"},
                    ),
                ),
                dbc.Col(
                    width=2,
                    children=dcc.RadioItems(
                        id="report-type-selection",
                        labelStyle={"display": "block"},
                    ),
                ),
                dbc.Col(
                    width=2,
                    children=dcc.RadioItems(
                        id="source-selection",
                        labelStyle={"display": "block"},
                    ),
                ),
            ],
            className="py-1",
        ),
        dbc.Row(children=dbc.Col(children=html.Div(id="product-info"))),
        dbc.Row(children=dbc.Col(children=dcc.Graph(id="graphic-tmp"))),
        dbc.Row(children=dbc.Col(children=dcc.Graph(id="graphic"))),
    ],
    fluid=True,
)


Selection = List[Dict[str, str]]


@app.callback(
    output=dict(
        regulation_options=Output("regulation-selection", "options"),
    ),
    inputs=dict(
        product=Input("product-selection", "value"),
    ),
)
def product_callback(  # type: ignore[no-untyped-def]
    product: str,
):  # note: doesn't work with annotated result type..?
    if not product:
        print(r"INFO: No product value. Ignoring callback.")
        return dash.no_update
    df: pd.DataFrame = tickers_ref_data[(tickers_ref_data["Product"] == product)]
    return dict(
        regulation_options=[
            {"label": i, "value": i} for i in df["Regulation"].unique()
        ],
    )


@app.callback(
    output=dict(
        report_type_options=Output("report-type-selection", "options"),
    ),
    inputs=dict(
        product=State("product-selection", "value"),
        regulation=Input("regulation-selection", "value"),
    ),
)
def regulation_callback(product: str, regulation: str) -> Dict[str, Selection]:
    df: pd.DataFrame = tickers_ref_data[
        (tickers_ref_data["Product"] == product)
        & (tickers_ref_data["Regulation"] == regulation)
    ]
    report_types: List[str] = df["ReportType"].unique().tolist()
    if len(report_types) == 1 and math.isnan(report_types[0]):  # type: ignore[arg-type]
        report_types = ["<none>"]
    return dict(
        report_type_options=[{"label": i, "value": i} for i in report_types],
    )


@app.callback(
    output=dict(
        report_type_options=Output("source-selection", "options"),
    ),
    inputs=dict(
        product=State("product-selection", "value"),
        regulation=State("regulation-selection", "value"),
        report_type=Input("report-type-selection", "value"),
    ),
)
def report_type_callback(
    product: str, regulation: str, report_type: str
) -> Dict[str, Selection]:
    df: pd.DataFrame = tickers_ref_data[
        (tickers_ref_data["Product"] == product)
        & (tickers_ref_data["Regulation"] == regulation)
    ]
    if report_type != "<none>":
        df = df[df["ReportType"] == report_type]
    sources: List[str] = df["Source"].unique().tolist()
    return dict(
        report_type_options=[{"label": i, "value": i} for i in sources],
    )


@app.callback(
    output=dict(
        product_info=Output("product-info", "children"),
        graphic=Output("graphic-tmp", "figure"),
    ),
    inputs=dict(
        product=State("product-selection", "value"),
        regulation=State("regulation-selection", "value"),
        report_type=State("report-type-selection", "value"),
        source=Input("source-selection", "value"),
    ),
)
def source_callback(  # type: ignore[no-untyped-def]
    product: str, regulation: str, report_type: str, source: str
):  # note: doesn't work with annotated result type..?
    if not product:
        print(r"INFO: No product value. Ignoring callback.")
        return dash.no_update
    start_time = time.perf_counter_ns()
    df: pd.DataFrame = tickers_ref_data[
        (tickers_ref_data["Product"] == product)
        & (tickers_ref_data["Regulation"] == regulation)
        & (tickers_ref_data["Source"] == source)
    ]
    if report_type != "<none>":
        df = df[df["ReportType"] == report_type]
    table = None
    if regulation == "CFTC":
        plot_index = [
            "TraderType",
            "AssetType",
            "Metric",
        ]
        if report_type == "All Disaggregated":
            table = mk_cftc_disaggregated(df)
        elif report_type == "All Legacy":
            table = mk_cftc_legacy(df)
    elif regulation == "MiFID":
        table = mk_mifid(df)
        plot_index = [
            "TraderType",
            "Activity",
            "Metric",
        ]
    assert table is not None
    table = table.applymap(  # type: ignore[operator]
        lambda x: rcm.lib.to_string_truncate_if_float(x, 2), na_action="ignore"
    )

    ts_tickers = df[
        functools.reduce(
            lambda a, b: a & b,
            (
                (df[idx] == val)
                for idx, val in zip(plot_index, df[plot_index].iloc[0].values)
            ),
        )
    ][
        [
            "Direction",
            "Ticker",
        ]
    ]
    timeseries = functools.reduce(
        lambda a, b: a.join(b, how="outer"),
        (
            get_timeseries(t, "Last").rename({"Last": d}, axis=1)
            for d, t in ts_tickers.values
        ),
    )
    timeseries.columns.name = "Direction"
    timeseries = timeseries.unstack()
    timeseries.name = "Value"
    timeseries = timeseries.reset_index()

    fig = px.line(
        timeseries,
        x="Date",
        y="Value",
        color="Direction"
    ).update_layout(
        margin={"t": 0, "l": 0, "r": 0, "b": 0}
    )  # remove top margins

    print(
        r"INFO: Elasped wall time for add_ticker callback: "
        f"{(time.perf_counter_ns() - start_time) / 1000000}ms"
    )
    return dict(
        product_info=dbc.Table.from_dataframe(table, hover=True, index=True),
        graphic=fig,
    )


################################################################################


def set_initial_option_value(options: Selection) -> Any:
    if options:
        return dict(value=options[0]["value"])
    else:
        # raise PreventUpdate
        return dash.no_update


@app.callback(
    output=dict(value=Output("regulation-selection", "value")),
    inputs=dict(options=Input("regulation-selection", "options")),
)
def set_initial_regulation_value(options: Selection) -> Any:
    return set_initial_option_value(options)


@app.callback(
    output=dict(value=Output("report-type-selection", "value")),
    inputs=dict(options=Input("report-type-selection", "options")),
)
def set_initial_report_type_value(options: Selection) -> Any:
    return set_initial_option_value(options)


@app.callback(
    output=dict(value=Output("source-selection", "value")),
    inputs=dict(options=Input("source-selection", "options")),
)
def set_initial_source_value(options: Selection) -> Any:
    return set_initial_option_value(options)


def main() -> None:
    app.run_server(debug=True, threaded=True)


if __name__ == "__main__":
    main()
