"""Generate dbc table from dataframe. Copied from dbc library."""
from functools import reduce
from itertools import groupby
from operator import add

from dash import html
import dash_bootstrap_components as dbc


def generate_table_from_df(
    df,
    float_format=None,
    columns=None,
    header=True,
    index=False,
    index_label=None,
    date_format=None,
    cell_type=None,
    cell_x_label_func=None,
    cell_y_label_func=None,
    **table_kwargs
):
    """
    Generate a Table component from a dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to render as a table.
    float_format : str, optional
        Format to use for floating point numbers.
    columns : sequence, optional
        Columns to render.
    header : boolean or list(str) or dict(str: str), optional
        Write out the column names. If a list of strings is given it is assumed
        to be aliases for the columns names (and hence must be the same length
        as df.columns). A dict can be passed to rename some columns, the format
        is {'<current_name>': '<new_name>'}. The dictionary need not have an
        entry for every column.
    index : boolean, optional
        Render the row names (index).
    index_label : str, optional
        Column label for index column if desired. If None is passed, but both
        header and index are True, then the index name is used.
    date_format : str, optional
        Format string for datetime objects.
    **table_kwargs : Keyword arguments
        Additional arguments to pass to the table component. See
        dash_bootstrap_components.Table for details.
    """
    import numpy as np
    import pandas as pd

    df = df.copy(deep=True)

    if columns is not None:
        df = df.loc[:, columns]

    if float_format is not None:
        for c in df.select_dtypes(["float"]).columns:
            df[c] = df[c].map(lambda x: "{1:{0}}".format(float_format, x))

    if date_format is not None:
        for c in df.select_dtypes(["datetime"]).columns:
            df[c] = df[c].map(lambda x: x.strftime(date_format))

    if index:
        df = df.reset_index()
        if index_label is not None:
            df = df.rename(columns={"index": index_label})

    if header:
        if isinstance(header, (tuple, list, np.ndarray, pd.Index)):
            try:
                df.columns = header
            except ValueError:
                raise ValueError(
                    "If specifying column names with a sequence, the number "
                    "of names must exactly match the number of columns."
                )
        elif isinstance(header, dict):
            df = df.rename(columns=header)

        # Get the actual headers
        n_levels = df.columns.nlevels
        header_values = [
            list(df.columns.get_level_values(level)) for level in range(n_levels)
        ]

        # The sizes of consecutive header groups at each level
        header_spans = [
            [len(list(group)) for _, group in groupby(level_values)]
            for level_values in header_values
        ]

        # The positions of header changes for each level as an integer
        header_breaks = [
            [sum(level_spans[:i]) for i in range(1, len(level_spans) + 1)]
            for level_spans in header_spans
        ]

        # Include breaks from higher levels
        header_breaks = [
            sorted(set(reduce(add, header_breaks[:level])).union({0}))
            for level in range(1, n_levels + 1)
        ]

        # Go from header break positions back to cell spans
        header_spans = [
            reversed(
                [
                    level_breaks[i] - level_breaks[i - 1]
                    for i in range(len(level_breaks) - 1, 0, -1)
                ]
            )
            for level_breaks in header_breaks
        ]

        table = [
            html.Thead(
                [
                    html.Tr(
                        children=[
                            html.Th(
                                header_values[level][pos],
                                colSpan=span,
                            )
                            for pos, span in zip(
                                header_breaks[level], header_spans[level]
                            )
                        ]
                    )
                    for level in range(n_levels)
                ]
            )
        ]
    else:
        table = []
    table.append(
        html.Tbody(
            [
                html.Tr(
                    [
                        html.Td(
                            df.iloc[i, j],
                            id={
                                "type": cell_type,
                                "x": cell_x_label_func(i) if cell_x_label_func else i,
                                "y": cell_y_label_func(j) if cell_y_label_func else j,
                            },
                        )
                        if cell_type
                        else html.Td(df.iloc[i, j])
                        for j in range(len(df.columns))
                    ]
                )
                for i in range(len(df))
            ]
        )
    )
    return dbc.Table(table, **table_kwargs)
