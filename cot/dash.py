"""Module"""
# pylint: disable=unused-import, missing-function-docstring

from typing import Optional, Tuple, Dict, List, Any

import cot.lib
import cot.dbc_table

import functools
import time
import math
import ast
import json

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL
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


def get_relevant_ref_data(product: str, regulation: str, report_type: Optional[str], source: str):  # type: ignore[no-untyped-def]
    product_ref: pd.DataFrame = tickers_ref_data[
        (tickers_ref_data["Product"] == product)
        & (tickers_ref_data["Regulation"] == regulation)
        & (tickers_ref_data["Source"] == source)
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


app.layout = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    width=7,
                    children=[
                        dcc.Dropdown(
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
                        html.Small(
                            r"(Initial loading of data is slow, for now. Please wait ~30s when viewing a dataset for the first time.)"
                        ),
                    ],
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
        dbc.Row(children=dbc.Col(children=html.H5(id="graphic-title"))),
        dbc.Row(children=dbc.Col(children=html.Div(id="graphic"))),
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

    df = get_relevant_ref_data(
        product, regulation, None if report_type == "<none>" else report_type, source
    )
    dftable = None
    if regulation == "CFTC":
        if report_type == "All Disaggregated":
            dftable = mk_cftc_disaggregated(df)
        elif report_type == "All Legacy":
            dftable = mk_cftc_legacy(df)
    elif regulation == "MiFID":
        dftable = mk_mifid(df)
    assert dftable is not None
    dftable = dftable.applymap(  # type: ignore[operator]
        lambda x: rcm.lib.to_string_truncate_if_float(x, 2), na_action="ignore"
    )

    print(
        r"INFO: Elasped wall time for source_callback: "
        f"{(time.perf_counter_ns() - start_time) / 1000000}ms"
    )
    dftable_idx = dftable.index
    dftable_cols = dftable.columns
    return dict(
        product_info=html.Div(
            [
                rcm.dbc_table.generate_table_from_df(
                    dftable,
                    hover=True,
                    index=True,
                    cell_type="product-table-cell",
                    cell_x_label_func=lambda i: str((i, dftable_idx[i][0])),
                    cell_y_label_func=lambda j: str(
                        # The index j is part of the key as react doesn't like it when
                        # two elemets have the same id.
                        (j, dftable_cols[j - 2][0], dftable_cols[j - 2][1])
                    )
                    if j >= 2
                    else f"<index>{j}",
                ),
                html.Small(
                    "Click on figures to see historical plot", style={"float": "right"}
                ),
            ]
        ),
    )


@app.callback(
    output=dict(
        graphic_title=Output("graphic-title", "children"),
        graphic=Output("graphic", "children"),
        #dbg_output=Output("dbg_output", "children"),
    ),
    inputs=dict(
        product=State("product-selection", "value"),
        regulation=State("regulation-selection", "value"),
        report_type=State("report-type-selection", "value"),
        source=State("source-selection", "value"),
        cell_click=Input(
            {"type": "product-table-cell", "x": ALL, "y": ALL}, "n_clicks"
        ),
    ),
)
def ticker_group_callback(
    product: str, regulation: str, report_type: str, source: str, cell_click: List[int]
):
    start_time = time.perf_counter_ns()

    ctx = dash.callback_context
    # Upon initial load, this callback is strangely triggered with [{'prop_id':
    # '.', 'value': None}]. So triggered[-1] always works.
    triggered_cell = ctx.triggered[-1]["prop_id"][:-9]  # remove ".n_clicks" suffix
    try:
        triggered_cell = ast.literal_eval(triggered_cell)
        triggered_cell["x"] = ast.literal_eval(triggered_cell["x"])
        triggered_cell["y"] = ast.literal_eval(triggered_cell["y"])
    except SyntaxError:
        print(r"INFO: No triggered cell. Ignoring callback.")
        return dash.no_update

    df = get_relevant_ref_data(
        product, regulation, None if report_type == "<none>" else report_type, source
    )
    if regulation == "CFTC":
        plot_index = {
            "TraderType": triggered_cell["x"][1],
            "AssetType": triggered_cell["y"][1],
            "Metric": triggered_cell["y"][2],
        }
    elif regulation == "MiFID":
        plot_index = {
            "TraderType": triggered_cell["x"][1],
            "Activity": triggered_cell["y"][1],
            "Metric": triggered_cell["y"][2],
        }
    else:
        raise Exception("Regulation type not recognised.")
    plot_title = triggered_cell["x"][1] + " / " + triggered_cell["y"][1]

    ts_tickers = df[
        functools.reduce(
            lambda a, b: a & b,
            ((df[idx] == val) for idx, val in plot_index.items()),
        )
    ][["Direction", "Ticker"]]
    if not len(ts_tickers):
        print(r"INFO: No data for triggered cell. Ignoring callback.")
        return dash.no_update
    timeseries = functools.reduce(
        lambda a, b: a.join(b, how="outer"),
        (
            get_timeseries(t, "Last").rename({"Last": d}, axis=1)
            for d, t in ts_tickers.values
        ),
    )
    timeseries.columns.name = "Direction"
    cols = timeseries.columns.tolist()
    if "Long" in cols and "Short" in cols:
        timeseries["Nett"] = timeseries["Long"] - timeseries["Short"]
        # rearrange such that "Nett" is always the 3rd column
        cols = cols[0:2] + ["Nett"] + cols[2:]
        timeseries = timeseries[cols]
    timeseries = timeseries.unstack()
    timeseries.name = plot_index["Metric"]
    timeseries = timeseries.reset_index()

    axis_format = dict(
        showline=False,
        zerolinecolor="rgb(100, 100, 100)",
        gridcolor="rgb(204, 204, 204)",
    )
    fig = px.line(
        timeseries,
        x="Date",
        y=plot_index["Metric"],
        color="Direction",
    ).update_layout(
        plot_bgcolor="white",
        margin={"t": 0, "l": 0, "r": 0, "b": 0},
        xaxis=axis_format,
        yaxis=axis_format,
    )

    print(
        r"INFO: Elasped wall time for ticker_group_callback: "
        f"{(time.perf_counter_ns() - start_time) / 1000000}ms"
    )
    return dict(
        graphic_title=plot_title,
        graphic=dcc.Graph(figure=fig),
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
