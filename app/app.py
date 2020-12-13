import numpy as np
import pandas as pd

import odditylib as od
import streamlit as st

import plotly.graph_objs as go

from typing import *

st.set_page_config(
    layout='wide'
)

Z_SCORE_INTERVALS = {
    0.99: 2.576,
    0.95: 1.960,
    0.90: 1.645,
    0.80: 1.282,
    0.50: 0.674
}

DEMO_DATA = {
    'set1': './data/multiTimeline1.csv',
    'set2': './data/multiTimeline2.csv',
    'set3': './data/multiTimeline3.csv',
    'set4': './data/multiTimeline4.csv',

}


@st.cache
def read_data(file_path: str, nrows: int = None) -> Tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(file_path, nrows=nrows)
    return df['timestamp'].values, df['value'].values


@st.cache
def train_oddity(data: np.ndarray, detector: od.Oddity) -> od.Oddity:
    detector.fit(data)

    return detector


@st.cache
def rank_anomalies(lower_bound: Union[List, np.ndarray], upper_bound: Union[List, np.ndarray],
                   y_data: Union[List, np.ndarray]) -> Tuple[Tuple[List, List], Tuple[List, List], Tuple[List, List]]:

    minor_dates, minor_values = [], []
    warning_dates, warning_values = [], []
    severe_dates, severe_values = [], []

    for i, point in enumerate(y_data):

        # Minor
        if lower_bound[i] - lower_bound[i] * 0.20 < point < lower_bound[i]:
            minor_dates.append(x[i])
            minor_values.append(point)
            continue

        if upper_bound[i] < point < upper_bound[i] * 1.20:
            minor_dates.append(x[i])
            minor_values.append(point)
            continue

        # Warning
        if lower_bound[i] - lower_bound[i] * 0.30 < point < lower_bound[i] - lower_bound[i] * 0.20:
            warning_dates.append(x[i])
            warning_values.append(point)
            continue

        if upper_bound[i] * 1.20 < point < upper_bound[i] * 1.30:
            warning_dates.append(x[i])
            warning_values.append(point)
            continue

        # Severe
        if point < lower_bound[i] - lower_bound[i] * 0.30 or point > upper_bound[i] * 1.30:
            severe_dates.append(x[i])
            severe_values.append(point)
            continue

    return (minor_dates, minor_values), (warning_dates, warning_values), (severe_dates, severe_values)


def add_vrect(figure: Union[go.Figure, go.FigureWidget], dates: Union[List, np.ndarray],
              anomalous_dates: Union[List, np.ndarray], fillcolor: str='Red', opacity: float=0.25):
    x0, x1 = dates[0], dates[-1]

    for date in anomalous_dates:

        try:
            x0 = x[dates.index(date) - 1]
        except IndexError:
            pass

        try:
            x1 = x[dates.index(date) + 1]
        except IndexError:
            pass

        figure.add_vrect(
            x0=x0, x1=x1,
            fillcolor=fillcolor, opacity=opacity,
            layer="above", line_width=0,
        )


if __name__ == '__main__':
    st.sidebar.title('Oddity Demo')
    st.sidebar.subheader('\n')

    st.sidebar.header('General Settings')

    selection = st.sidebar.selectbox('Demo Data', ['set1', 'set2', 'set3', 'set4'])
    options = st.sidebar.multiselect('Filter Severity', ['Severe', 'Warning', 'Minor'],
                                     default=['Severe', 'Warning', 'Minor'])

    st.sidebar.header('Oddity Training Settings')
    trend_kernel = st.sidebar.selectbox('Trend Kernel', options=['rbf', 'periodic', 'locally periodic'])

    trend_l, trend_sigma = st.sidebar.slider('Trend l factor', value=10.0, min_value=0.01, max_value=50.0), \
                           st.sidebar.slider('Trend sigma factor', value=2.0, min_value=0.01, max_value=10.0)

    season_kernel = st.sidebar.selectbox('Seasonal Kernel', options=['rbf', 'periodic', 'locally periodic'], index=1)

    season_l, season_sigma = st.sidebar.slider('Seasonality l factor', value=1.0, min_value=0.01, max_value=50.0), \
                             st.sidebar.slider('Seasonality sigma factor', value=0.25, min_value=0.01, max_value=10.0)

    x, y = read_data(DEMO_DATA[selection])

    oddity = train_oddity(y.reshape(-1, 1), od.Oddity(params={
        'trend':
            {'kernel': trend_kernel,
             'l': trend_l,
             'sigma_y': trend_sigma},
        'seasonal':
            {'kernel': 'periodic',
             'l': season_l,
             'sigma_y': season_sigma}
    } if not st.sidebar.button('Retrain with Default') else None))

    mu, cov = oddity.mu, oddity.cov

    x = x.ravel()
    mu = mu.ravel()
    uncertainty = (Z_SCORE_INTERVALS[0.95] * np.sqrt(np.diag(cov)) + 3) ** 2

    upper, lower = (mu + uncertainty), (mu - uncertainty)

    minors, warnings, severe = rank_anomalies(lower, upper, y)

    x, y = x.tolist(), y.tolist()

    fig = go.FigureWidget([
        go.Scatter(
            x=x,
            y=y,
            line=dict(color='rgb(16, 159, 199)'),
            mode='lines'
        ),
        go.Scatter(
            name='Upper Bound',
            x=x,
            y=upper,
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=x,
            y=lower,
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(124, 211, 235, 0.3)',
            fill='tonexty',
            showlegend=False
        ),
        go.Scatter(
            name='Severe',
            x=severe[0] if 'Severe' in options else [],
            y=severe[1],
            mode='markers',
            marker=dict(
                color='Red',
                size=12,
                line=dict(
                    color='Black',
                    width=2
                )
            ),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Warning',
            x=warnings[0] if 'Warning' in options else [],
            y=warnings[1],
            mode='markers',
            marker=dict(
                color='rgb(237, 223, 58)',
                size=12,
                line=dict(
                    color='Black',
                    width=2
                )
            ),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Minor',
            x=minors[0] if 'Minor' in options else [],
            y=minors[1],
            mode='markers',
            marker=dict(
                color='LightSkyBlue',
                size=12,
                line=dict(
                    color='Black',
                    width=2
                )
            ),
            line=dict(width=0),
            showlegend=False
        ),
    ])

    fig.update_xaxes(rangeslider_visible=True)

    SEVERITIES = {
        'Severe': [fig, x, severe[0], 'Red', 0.1],
        'Warning': [fig, x, warnings[0], 'rgb(237, 223, 58)', 0.35],
        'Minor': [fig, x, minors[0], 'LightSkyBlue', 0.25]
    }

    for severity in options:
        add_vrect(*SEVERITIES[severity])

    fig.update_layout(width=2000, height=1000)
    st.plotly_chart(fig, use_container_width=True)
