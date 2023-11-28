# import desired libraries
import pandas as pd
import plotly.io as pio
pio.templates.default = "simple_white"
import pathlib
import plotly.graph_objects as go
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
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

def composition_dash():
    tot = final_df.groupby('BUILDING_NUMBER')['FAIL'].sum()
    bldb01 = final_df[final_df.BUILDING_NUMBER == "B01"].groupby('LINE_NUMBER')['FAIL'].sum()
    bldb02 = final_df[final_df.BUILDING_NUMBER == "B02"].groupby('LINE_NUMBER')['FAIL'].sum()
    lineA = final_df[final_df.LINE_NUMBER == "A"].groupby('TECHNICIAN_ID')['FAIL'].sum()
    lineB = final_df[final_df.LINE_NUMBER == "B"].groupby('TECHNICIAN_ID')['FAIL'].sum()
    lineC = final_df[final_df.LINE_NUMBER == "C"].groupby('TECHNICIAN_ID')['FAIL'].sum()
    lineD = final_df[final_df.LINE_NUMBER == "D"].groupby('TECHNICIAN_ID')['FAIL'].sum()

    # %%
    source = [0, 0, 1, 1,  # B01 -> A, B01 -> B, B02 -> C, B02 -> D
              2, 2, 2, 2, 2, 2, 2,  # A -> T000, A -> T010, ..., A -> T015
              3, 3, 3, 3, 3, 3, 3,  # B -> T000, B -> T010, ..., B -> T015
              4, 4, 4, 4, 4, 4, 4,  # C -> T000, C -> T010, ..., C -> T015
              5, 5, 5, 5, 5, 5, 5]  # D -> T000, D -> T010, ..., D -> T015

    target = [2, 3, 4, 5,  # Targets for flows from B01 and B02
              6, 7, 8, 9, 10, 11, 12,  # Targets for flows from A
              6, 7, 8, 9, 10, 11, 12,  # Targets for flows from B
              6, 7, 8, 9, 10, 11, 12,  # Targets for flows from C
              6, 7, 8, 9, 10, 11, 12]

    value = [bldb01.A, bldb01.B, bldb02.C, bldb02.D,  # Targets for flows from B01 and B02
             lineA.T000, lineA.T010, lineA.T011, lineA.T012, lineA.T013, lineA.T014, lineA.T015,
             # Targets for flows from A
             lineB.T000, lineB.T010, lineB.T011, lineB.T012, lineB.T013, lineB.T014, lineB.T015,
             # Targets for flows from B
             lineC.T000, lineC.T010, lineC.T011, lineC.T012, lineC.T013, lineC.T014, lineC.T015,
             # Targets for flows from C
             lineD.T000, lineD.T010, lineD.T011, lineD.T012, lineD.T013, lineD.T014, lineD.T015]
    fig3 = go.Figure(go.Sankey(
        arrangement="snap",
        node={
            "label": ["B01", "B02", "A", "B", "C", "D", "T000", "T010", "T011", "T012", "T013", "T014", "T015"],
            "x": [0.1, 0.1, 0.4, 0.4, 0.4, 0.4, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
            "y": [0.2, 0.4, 0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
            "color": [CFG.main_color, CFG.main_color, CFG.color2, CFG.color2, CFG.color2, CFG.color2, CFG.color3,
                      CFG.color3, CFG.color3, CFG.color3, CFG.color3, CFG.color3, CFG.color3],
            'pad': 20},  # 10 Pixels
        link={
            "source": source,
            "target": target,
            "value": value}))
    fig3.update_layout(title='Defective Widgets Manufacturing Flow')

    value = [tot.B01, tot.B02, bldb01.A, bldb01.B, bldb02.C, bldb02.D]
    labels = ["Virginia ISI", "B01", "B02", "A", "B", "C", "D"]
    parents = ["", "Virginia ISI", "Virginia ISI", "B01", "B01", "B02", "B02"]
    colors = [CFG.color2, CFG.main_color, CFG.main_color, CFG.color3, CFG.color3, CFG.color3, CFG.color3]
    fig1 = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=[final_df.FAIL.sum()] + value,
        branchvalues="total",
        marker=dict(colors=colors)
    ))

    fig1.update_layout(showlegend=False, title='Hierarchical View')

    col = 'LINE_NUMBER'
    pareto_df = final_df.groupby(col)['FAIL'].sum().reset_index()
    pareto_df = pareto_df.sort_values(by='FAIL', ascending=False)
    pareto_df['CumulativePercentage'] = pareto_df['FAIL'].cumsum() / pareto_df['FAIL'].sum() * 100
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=pareto_df[col], y=pareto_df['FAIL'], name='Number of Defects', marker_color=CFG.color2))
    fig2.add_trace(
        go.Line(x=pareto_df[col], y=pareto_df['CumulativePercentage'], name='Cumulative Percentage', yaxis='y2',
                line=dict(color=CFG.color3, width=3)))
    fig2.update_layout(
        title=f'Defects by {col.replace("_", " ").capitalize()}',
        yaxis=dict(title='Defect Count'),
        xaxis=dict(title=col.replace("_", " ").capitalize()),
        yaxis2=dict(title='Cumulative Percentage', overlaying='y', side='right'),
        showlegend=False
    )


    return fig1, fig2, fig3


fig1, fig2, fig3 = composition_dash()




app = dash.Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width"}])

layout = dbc.Container(
    [dbc.Row(dbc.Col(html.H3('Manufacturing Process Overview', className='text-center text-primary, mb-3'))),

     dbc.Row([
         dbc.Col([
             dcc.Graph(id='fig1c', figure=fig1,
                       style={'height': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 1}),
         dbc.Col([
             dcc.Graph(id='fig2c', figure=fig2,
                       style={'height': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 2})],
         align="center"),

     dbc.Row([
         dbc.Col([
             dcc.Graph(id='fig3c', figure=fig3,
                       style={'height': 600}),
             html.Hr()
         ], width={'size': 12, 'offset': 0, 'order': 1})])])

