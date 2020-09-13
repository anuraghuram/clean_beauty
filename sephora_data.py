# -------------------------
# Filename: sephora_data.py
# Author: Anu R
# Created: Sept 2020
# Python version: 3.7
# -------------------------

import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import plotly.io as pio
from params import *


def product_filter(sample: pd.DataFrame):
    """
    This function:
     1. Recodes products into one of six broad categories: BODY, LIPS, EYES, FACE, HAIR or OTHER
     2. Allows user to filter further from the size recoded categories e.g. return df with LIPS and FACE products only

    :param sample: A pandas DataFrame
    :return: A pandas DataFrame with recoded product categories
    """
    df = sample.copy()

    # Recode products into broader categories
    conversion_keys = []
    conversion_vals = []
    for broader_cat, products in recoded_cats.items():
        for p in products:
            conversion_keys.append(p)
            conversion_vals.append(broader_cat)
    conversion_dict = dict(zip(conversion_keys, conversion_vals))
    df['category'] = df['category'].replace(conversion_dict)

    if filter_products:
        df = df[df['category'].isin(filter_products)]

    return df


def ingredient_filter(sample: pd.DataFrame):
    """
    This function filters products by specified ingredients
    :param sample: A pandas DataFrame
    :return: A pandas DataFrame filtered by specified ingredients
    """
    df = sample.copy()

    if filter_ingredients:
        df = df[df['ingredients'].isin(filter_ingredients)]

        for f in filter_ingredients:
            if f not in df['ingredients']:
                raise Exception('Ingredient not found: '+f)

    if clean_tag_filter:
        df = df[df['ingredients'].str.contains('Clean at Sephora')]
    else:
        df = df[~df['ingredients'].str.contains('Clean at Sephora')]

    return df


def stacked_bar_chart(sample: pd.DataFrame, grouper_col: str, x: str, y: str, orientation: str,
                      color_col: str, x_title: str, y_title: str, main_title: str, file: str):
    """
    :param sample: A pandas DataFrame
    :param grouper_col:
    :param x: Column from which x values will be derived
    :param y: Column from which y values will be derived
    :param orientation: Either 'v' or 'h' for a vertical or horizontal orientation respectively
    :param color_col: Column with values to use as colour traces
    :param x_title: String for x axis title
    :param y_title: String for y axis title
    :param main_title: String to input as chart title
    :param file: String representing .png filename
    :return: A plot.ly graph objects figure
    """
    df = sample.copy()
    df = df.sort_values(color_col)

    pio.templates.default = 'plotly_white'
    color_map = color_formatter(sample=df, color_col=color_col)

    chart = px.bar(data_frame=df, x=x, y=y, color=color_col, orientation=orientation, color_discrete_map=color_map, title=main_title)

    # To ensure that bar heights are arranged in order
    df_grouped_for_ordering = df.groupby([grouper_col]).sum().reset_index()
    df_grouped_for_ordering = df_grouped_for_ordering.sort_values(by=[x], ascending=True)
    array_ordering = df_grouped_for_ordering['brand'].values
    chart.update_layout(barmode='stack', yaxis={'categoryorder': 'array', 'categoryarray': array_ordering})

    chart.update_xaxes(title_text=x_title, showgrid=False, tickfont=dict(family='Arial', color='Black', size=12), zeroline=False)
    chart.update_yaxes(title_text=y_title, showgrid=False, tickfont=dict(family='Arial', color='Black', size=12), zeroline=False)

    chart_formatter(chart=chart, main_title=main_title, legend_pos=-0.15)
    pio.write_image(fig=chart, file=filepath+file+'.png')

    return chart


def dual_axis_bar(sample: pd.DataFrame, x: str, y1: str, y2: str, legend_y1: str, legend_y2: str,
                  y1_title: str, y2_title: str, main_title: str, file: str):
    """
    :param sample: A pandas DataFrame
    :param x: Column from which x values will be derived
    :param y1: Column from which primary y values will be derived
    :param y2: Column from which secondary y values will be derived
    :param legend_y1: String for legend key representing primary y measure
    :param legend_y2: String for legend key representing secondary y measure
    :param y1_title: String for primary y axis title
    :param y2_title: String for secondary y axis title
    :param main_title: String to input as chart title
    :param file: String representing .png filename
    :return: A plot.ly graph objects figure
    """

    df = sample.copy()

    pio.templates.default = 'plotly_white'

    chart = go.Figure(
            data=[
                go.Bar(name=legend_y1, x=df[x], y=df[y1], yaxis='y', offsetgroup=1, marker_color='rgb(250, 180, 174)'),
                go.Bar(name=legend_y2, x=df[x], y=df[y2], yaxis='y2', offsetgroup=2, marker_color='rgb(179, 205, 227)')
            ],
            layout={
                'yaxis': {'title': y1_title},
                'yaxis2': {'title': y2_title, 'overlaying': 'y', 'side': 'right'}
            }
    )
    chart.update_layout(barmode='group')
    chart.update_xaxes(showgrid=False)
    chart.update_yaxes(showgrid=False)
    chart_formatter(chart=chart, main_title=main_title, legend_pos=-0.25)
    pio.write_image(fig=chart, file=filepath+file+'.png')

    return chart


def box_plot(sample: pd.DataFrame, x: str, y: str, x_title: str, y_title: str, main_title: str, file: str):
    """
    :param sample: A pandas DataFrame
    :param x: Column from which x values will be derived
    :param y: Column from which y values will be derived
    :param x_title: String for x axis title
    :param y_title: String for y axis title
    :param main_title: String to input as chart title
    :param file: String representing .png filename
    :return: A plot.ly graph objects figure
    """
    df = sample.copy()

    # To ensure legend keys are in a consistent order across charts
    if x.isalpha():
        df = df.sort_values(x)

    pio.templates.default = 'plotly_white'
    color_map = color_formatter(sample=df, color_col=x)

    chart = px.box(df, x=x, y=y, color=x, color_discrete_map=color_map)
    chart.update_xaxes(title_text=x_title, showgrid=False, tickfont=dict(family='Arial', color='Black', size=12), zeroline=False)
    chart.update_yaxes(title_text=y_title, showgrid=False, tickfont=dict(family='Arial', color='Black', size=12), zeroline=False)
    chart_formatter(chart=chart, main_title=main_title, legend_pos=-0.15)
    pio.write_image(fig=chart, file=filepath+file+'.png')

    return chart


def chart_formatter(chart: go.Figure, main_title: str, legend_pos: float):
    """
    This function formats chart dimensions, legend and title text
    :param chart: A plot.ly graph objects figure
    :param main_title: String to input as chart title
    :param legend_pos: Float to adjust positioning of the legend below the chart
    :return:
    """
    chart.update_layout(legend=dict(orientation='h', yanchor='bottom', y=legend_pos, xanchor='center', x=0.5))
    chart.update_layout(title=main_title, legend_title_text='')
    chart.update_layout(font_family='Arial', font_color='Black', title_font_family='Arial', title_font_color='Black', legend_title_font_color='Black')
    chart.update_layout(autosize=False, width=800, height=600)

    return chart


def color_formatter(sample: pd.DataFrame, color_col: str):
    """
    This function produces a dictionary of colours for each unique trace to be inputted
    into the color_discrete_map parameter in a px.line or px.bar chart
    :param sample: A pandas DataFrame
    :param color_col: Column from which traces will be derived
    :return: A dict containing a key (string value of the trace name) and a corresponding colour to assign to the trace
    """
    df = sample.copy()
    traces = sorted(df[color_col].unique().tolist())
    colorway = px.colors.qualitative.Pastel1[:len(traces)]

    color_map = {}
    for t, c, in zip(traces, colorway):
        color_map[t] = c

    return color_map

