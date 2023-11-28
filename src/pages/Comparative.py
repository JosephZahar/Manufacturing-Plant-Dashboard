# import desired libraries
import pandas as pd
import plotly.io as pio
pio.templates.default = "simple_white"
import pathlib
import plotly.graph_objects as go
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import dash
import plotly.express as px

import warnings
warnings.filterwarnings("ignore")

PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()

class CFG:
    data_dir = "data/"
    main_color = '#072B54'
    color2 = '#1a53ff'
    color3 = '#E67A27'
    color4 = '#55B7DA'
    color5 = '#CD3610'

field_df = pd.read_csv(DATA_PATH.joinpath("field.csv"))
mfg_df = pd.read_csv(DATA_PATH.joinpath("mfg.csv"))
# beer_df = pd.read_csv(CFG.data_dir + "monthly-beer-production-in-austr.csv")
# beer_df['Month'] = pd.to_datetime(beer_df['Month'])
# beer_df.set_index('Month', inplace=True)
# beer_df.index.freq = 'MS'
field_df2 = field_df.dropna()
mfg_df2 = mfg_df.dropna()
field_df3 = field_df2[field_df2.SERIAL_NUMBER != '0000000000000000']
mfg_df3 = mfg_df2[mfg_df2.SERIAL_NUMBER != '0000000000000000']
final_df = field_df3.merge(mfg_df3, how='inner', on='SERIAL_NUMBER')
def time_cols(cols):
    for col in cols:
        final_df[col] = pd.to_datetime(final_df[col])
        final_df[col+ '_YMD'] = final_df[col].dt.strftime('%Y-%m-%d')
        final_df[col+ '_YM'] = final_df[col].dt.strftime('%Y-%m')
time_cols(['USE_TIME', 'MFG_TIME'])



def comparative_dash(line_number):
    df = final_df.copy()
    if line_number != 'All':
        df1 = df[df.LINE_NUMBER==line_number]
    else:
        df1 = df.copy()

    color_map = {
        0: CFG.color2,
        1: CFG.color3,
    }

    fig1 = px.histogram(df1, x="HUMIDITY", color="FAIL", color_discrete_map=color_map)
    fig1.update_layout(
        title=f'Widgets with defects vs Humidity',
        yaxis=dict(title='Number of Widgets'),
        xaxis=dict(title='Humidity', overlaying='y', side='right'),
        showlegend=False
    )

    fig2 = px.histogram(df1, x="APPARATUS_TEMP", color="FAIL", color_discrete_map=color_map)
    fig2.update_layout(
        title=f'Widgets with defects vs Apparatus Temperature',
        yaxis=dict(title='Number of Widgets'),
        xaxis=dict(title='Temperature', overlaying='y', side='right'),
        showlegend=False
    )

    mfg_tm = df1.groupby('MFG_TIME_YMD').agg(
        {'FAIL': 'sum', 'HUMIDITY': 'mean', 'APPARATUS_TEMP': 'mean'}).reset_index()
    fig3 = make_subplots(rows=2, cols=1, vertical_spacing=0.08, row_heights=[0.7, 0.3])
    fig3.add_trace(go.Scatter(x=mfg_tm.MFG_TIME_YMD, y=mfg_tm['HUMIDITY'], mode='lines', name='Manufactured',
                             line_color=CFG.main_color), row=1, col=1)
    fig3.add_trace(go.Scatter(x=mfg_tm.MFG_TIME_YMD, y=mfg_tm['FAIL'], mode='lines', name='Used', line_color=CFG.color3),
                  row=2, col=1)
    fig3.update_xaxes(showticklabels=False, row=1, col=1)
    fig3.update_layout(height=500, yaxis=dict(title='Average Humidity'), yaxis2=dict(title='Defect Count'), showlegend=False)

    fig4 = make_subplots(rows=2, cols=1, vertical_spacing=0.08, row_heights=[0.7, 0.3])
    fig4.add_trace(go.Scatter(x=mfg_tm.MFG_TIME_YMD, y=mfg_tm['APPARATUS_TEMP'], mode='lines', name='Manufactured',
                             line_color=CFG.main_color), row=1, col=1)
    fig4.add_trace(go.Scatter(x=mfg_tm.MFG_TIME_YMD, y=mfg_tm['FAIL'], mode='lines', name='Used', line_color=CFG.color3),
                  row=2, col=1)
    fig4.update_xaxes(showticklabels=False, row=1, col=1)
    fig4.update_layout(height=500, yaxis=dict(title='Average Temperature'), yaxis2=dict(title='Defect Count'), showlegend=False)


    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=df1.MFG_TIME_YMD,
        y=df1.APPARATUS_TEMP,
        mode='markers',
        marker=dict(
            color=[color_map[val] for val in df1.FAIL],  # Apply the color map
            showscale=False, opacity=0.6  # No color scale for categorical data
        )
    ))
    # fig.add_trace(go.Line(x=final_df.MFG_TIME_YMD,y=final_df.fail2,
    #                       line=dict(color=CFG.color5, width=3)))
    fig5.update_layout(
        title=f'Apparatus temperature and defects over time',
        yaxis=dict(title='Appartus Temperature (F)'),
        showlegend=False
    )

    return fig1, fig2, fig3, fig4, fig5



fig1, fig2, fig3, fig4, fig5 = comparative_dash('All')

line_dropdown = dcc.Dropdown(options=["A", "B", "C", "D", 'All'],
                                id='line_namee',
                                clearable=False,
                                value='All', className="dbc",
                                placeholder='Select an Account', maxHeight=400)


app = dash.Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width"}])

layout = dbc.Container(
    [dbc.Row(dbc.Col(html.H3('Root Cause Analysis', className='text-center text-primary, mb-3'))),
     dbc.Row([dbc.Col(line_dropdown)]),
     dbc.Row([
         dbc.Col([
             dcc.Graph(id='fig1d', figure=fig1,
                       style={'height': 500,'width': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 1}),
         dbc.Col([
             dcc.Graph(id='fig3d', figure=fig3,
                       style={'height': 500, 'width': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 2})],
         align="center"),
dbc.Row([
         dbc.Col([
             dcc.Graph(id='fig2d', figure=fig2,
                       style={'height': 500,'width': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 1}),
         dbc.Col([
             dcc.Graph(id='fig4d', figure=fig4,
                       style={'height': 500, 'width': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 2})],
         align="center"),

     dbc.Row([
         dbc.Col([
             dcc.Graph(id='fig5d', figure=fig5,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 14, 'offset': 0, 'order': 1})])])




