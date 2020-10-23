# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
import altair as alt

RED = '#D32F2F'
YELLOW = '#FFCA28'
ORANGE = '#F57C00'
LIGHT_ORANGE = '#FFAB00'
GREEN = '#7CB342'


@st.cache()
def get_df():
    return pd.read_parquet('data/awair.parquet')


def score_color(x):
    if x <= 60:
        return RED
    elif x <= 80:
        return ORANGE
    else:
        return GREEN


def temp_color(x):
    if x <= 48:
        return RED
    elif x <= 51:
        return ORANGE
    elif x <= 62:
        return LIGHT_ORANGE
    elif x <= 64:
        return YELLOW
    elif x <= 77:
        return GREEN
    elif x <= 79:
        return YELLOW
    elif x <= 89:
        return LIGHT_ORANGE
    elif x <= 92:
        return ORANGE
    else:
        return RED


def humid_color(x):
    if x <= 15:
        return RED
    elif x <= 20:
        return ORANGE
    elif x <= 35:
        return LIGHT_ORANGE
    elif x <= 40:
        return YELLOW
    elif x <= 50:
        return GREEN
    elif x <= 60:
        return YELLOW
    elif x <= 65:
        return LIGHT_ORANGE
    elif x <= 80:
        return ORANGE
    else:
        return RED


def co2_color(x):
    if x <= 600:
        return GREEN
    elif x <= 1000:
        return YELLOW
    elif x <= 1500:
        return LIGHT_ORANGE
    elif x <= 2500:
        return ORANGE
    else:
        return RED


def voc_color(x):
    if x <= 333:
        return GREEN
    elif x <= 1000:
        return YELLOW
    elif x <= 3333:
        return LIGHT_ORANGE
    elif x <= 8332:
        return ORANGE
    else:
        return RED


def pm25_color(x):
    if x <= 15:
        return GREEN
    elif x <= 35:
        return YELLOW
    elif x <= 55:
        return LIGHT_ORANGE
    elif x <= 75:
        return ORANGE
    else:
        return RED


if __name__ == '__main__':
    st.beta_set_page_config(
        page_title="awair",
        layout="wide",
        page_icon="https://assets.website-files.com/5e740636238c35d731ff790a/5ebb634dacf6431494a020e0_awair.ico"  # noqa
    )
    st.header("Awair Sensor Data")

    df = get_df().round(2)
    dfr = df.reset_index()

    dfr['score_color'] = dfr['score'].apply(score_color)
    dfr['temp_color'] = dfr['temp'].apply(temp_color)
    dfr['humid_color'] = dfr['humid'].apply(humid_color)
    dfr['co2_color'] = dfr['co2'].apply(co2_color)
    dfr['voc_color'] = dfr['voc'].apply(voc_color)
    dfr['pm25_color'] = dfr['pm25'].apply(pm25_color)

    sensors = st.sidebar.multiselect(
        "Select Sensors",
        options=list(df.columns),
        default=list(df.columns),
    )

    min_dt = df.index.min().date()
    max_dt = df.index.max().date()
    dt = max_dt - pd.Timedelta("7D")

    from_dt = st.sidebar.date_input("From Date", value=dt, min_value=min_dt, max_value=max_dt)
    to_dt = st.sidebar.date_input("From Date", value=max_dt, min_value=min_dt, max_value=max_dt)

    df2 = dfr[(dfr['timestamp'].dt.date >= from_dt) & (dfr['timestamp'].dt.date <= to_dt)]

    st_cols = st.beta_columns(2)

    for i, s in enumerate(sensors):
        st_cols[i % 2].subheader(f"Average {s}: {round(df2[s].mean())}")

        chart = alt.Chart(df2).mark_circle().encode(
            x=alt.X('timestamp:T', axis=alt.Axis(format="%m/%d/%y %H:%M")),
            y=alt.Y(f'{s}:Q', scale=alt.Scale(domain=[df2[s].min(), df2[s].max()])),
            color=alt.Color(f'{s}_color', scale=None),
            tooltip=['timestamp', f'{s}:Q'],
        ).interactive()

        st_cols[i % 2].altair_chart(chart, use_container_width=True)
