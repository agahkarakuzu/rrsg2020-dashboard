import numpy as np
import matplotlib.pyplot as plt
import math
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.cm as m_cmap
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import dash_daq as daq
import dash_bootstrap_components as dbc
import matplotlib.colors as m_colors
import pandas as pd
from apps import home
import imageio
import nibabel as nib
from app import app, get_dataframe_brain
import os

# ==========================================================
# SIMPLE BRAIN VIEWER | CC GENU, CC SPLENIUM, GM, Deep GM
# ==========================================================
def get_roi_idx(img,lbl_idx,lbl_name): 
    dct = {}
    tmp = np.where(img==lbl_idx)
    idx = list(zip(tmp[0],tmp[1]))
    [dct.update({cur:lbl_name}) for cur in idx]
    return dct

def get_brain_lookup(list_in,map_name):
    list_in.append(0)
    cmap = m_cmap.get_cmap(map_name)
    norm = m_colors.Normalize(vmin=np.min(list_in),vmax=np.max(list_in))
    colors = []
    for ii in list_in:
        tmp =  list((np.array(cmap(norm(ii)))*255).astype('uint8'))
        cur_color = 'rgba(' + str(tmp[0]) + ',' + str(tmp[1]) + ',' + str(tmp[2]) + ','+ str(1) + ')'
        colors.append([norm(ii),cur_color])
    #colors[0] = [0, 'rgba(6,6,6,1)']
    print(colors)    
    return colors  

rrsg_brain = dict()
IMG = nib.load('rrsg_brain-label.nii.gz')
IMG = np.asanyarray(IMG.dataobj)
IMG = np.rot90(np.squeeze(IMG),1)
IMG[IMG==1] = 10
IMG[IMG==7] = 1
IMG[IMG==10] = 7

rrsg_brain.update(get_roi_idx(IMG,7,'T1 - cortical GM'))
rrsg_brain.update(get_roi_idx(IMG,2,'T1 - genu (WM)'))
rrsg_brain.update(get_roi_idx(IMG,3,'T1 - splenium (WM)'))
rrsg_brain.update(get_roi_idx(IMG,4,'T1 - deep GM'))
rrsg_brain.update(get_roi_idx(IMG,1,'Ventricles'))

# Dash DAQ dark theme wrapper theme colors
theme =  {
    'dark': True,
    'detail': '#fec02f',
    'primary': '#fcce62',
    'secondary': '#6E6E6E'
}

# STYLE TABS 
tab_style = {"background-color":"#fec02f",
             "margin-left":"2px",
             "border-radius": "5px 5px 0px 0px",
             "cursor":"grab"}

tab_style_home = {"background-color":"#e84855",
                  "margin-left":"2px",
                  "border-radius": "5px 5px 0px 0px",
                  "cursor":"grab"}

# _______  _______  _______  _______ 
#(  ____ \(  ___  )(  ____ )(  ____ \
#| (    \/| (   ) || (    )|| (    \/
#| |      | |   | || (____)|| (__    
#| |      | |   | ||     __)|  __)   
#| |      | |   | || (\ (   | (      
#| (____/\| (___) || ) \ \__| (____/\
#(_______/(_______)|/   \__/(_______/
                                                                        
# R O O T  L A Y O U T ---------------------------------------------------
# ========================================================================
# DATAFRAME WILL BE LOADED AND CACHED ONLY AT THE OPENING
# FIXME: HOME WILL BE AN EXTERNAL LINK
rootLayout = html.Div(
    [
        dbc.Tabs(
            [    dbc.Tab(label = 'Home',tab_id="home", tab_style=tab_style_home,label_style={"color": "white"}),
                 dbc.Tab(label="Big Picture",tab_id="big-picture-brain",tab_style=tab_style,label_style={"color": "white"}),
                 dbc.Tab(label="By Region",tab_id="by-region",tab_style=tab_style,label_style={"color": "white"}),
                 dbc.Tab(label="By Site",tab_id="by-site-brain",tab_style=tab_style,label_style={"color": "white"})
                 
            ],
            id="tabs-brain",
            active_tab="big-picture-brain",
        ),
        html.Div(id="content-brain"),
    ]
)

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| SERVE LAYOUT 
# =========================================================================
layout =  html.Div(children=[
             html.Div(id='dark-theme-components', 
                      children=[
                daq.DarkThemeProvider(theme=theme, 
                                      children=rootLayout)
                    ]),
             ])
# =========================================================================

# M A I N - T A B  S W I T C H  C A L L B A C K --------------------------
# =========================================================================
@app.callback([Output("content-brain", "children"),Output('tabs-brain','style')], [Input("tabs-brain", "active_tab"),Input('session-id', 'children')])
def switch_tab(at,session_id):
    if at == "big-picture-brain":
        df = get_dataframe_brain(session_id)
        df = df.round(2) # Set precision 
        return [tab1_Layout,{'visibility':'visible'}]
    elif at == "by-region":
        return [tab2_Layout,{'visibility':'visible'}]
    elif at == "by-site-brain":
        print('by site')
    elif at == "home":
        return [home.layout,{'visibility':'hidden','height':'0px'}]

# Create an empty figure that is coherent with the theme
empty_figure = go.Figure(layout={
  'plot_bgcolor':"#060606",
  'paper_bgcolor':"#060606",
  "xaxis":{"showgrid":False,"zeroline":False,"showticklabels":False},
  "yaxis":{"showgrid":False,"zeroline":False,"showticklabels":False}})

region_name = html.Div(id='region-name',children=[])

brainav = go.Figure(go.Heatmap(z=IMG,showscale = False,
                   colorscale = [[0,'rgb(6,6,6)'],[0.2,'#6C6F7F'],[0.3,'#4BC6B9'],[0.5,'#8e0045'],[0.6,'#3bc14a'],[1,'#c2a878']],hoverinfo='text'))
brainav.update_layout(plot_bgcolor="#060606", 
                      paper_bgcolor="#060606",
                      xaxis = {"showgrid":False,"zeroline":False,"showticklabels":False},
                      yaxis = {"showgrid":False,"zeroline":False,"showticklabels":False},
                      height = 400,
                      width = 360,
                      margin=dict(l=0, r=0, t=10, b=0),
                      shapes = [dict(
                                type="rect",
                                x0=366,
                                y0=309,
                                x1=386,
                                y1=329,
                                fillcolor="#fec02f",
                                layer="above",
                                opacity=1,
                                line_width=1)],
                    annotations = [
                                dict(
                                    x = 376,
                                    y = 319,
                                    text = "Representative ROI",
                                    font = dict(color='#fec02f'),
                                    showarrow = True,
                                    arrowhead = 7,
                                    ax = 50,
                                    ay = -40
                                )
                                  ]
                    )


brain_cockpit = dcc.Graph(
        id='fig-brain',
         figure=brainav,
         config={
        'displayModeBar': False    
        },
        style={'cursor':'grab'})

led_tesla_brain = daq.LEDDisplay(
    label="Field Strength (T)",
    value='3.00',
    color="#fec02f",
    id = 'led-tesla-brain'
)

led_avg_brain = daq.LEDDisplay(
    label="T1 Mean (ms)",
    value='3.00',
    color="#fec02f",
    id = 'led-avg-brain'
)

led_std_brain = daq.LEDDisplay(
    label="T1 STD",
    value='3.00',
    color="#fec02f",
    id = 'led-std-brain'
)

vendor_brain_t1 = dcc.Slider(
    min=0,
    max=3,
    step=1,
    marks={
        0: 'All',
        1: 'Siemens',
        2: 'GE',
        3: 'Philips',
    },
    value=0,
    id='vendor-slider'
)

# The gauge to show # of scans (after selection)
guage_brain = daq.Gauge(
      id='guage-brain',
      min=0,
      max=56,
      value=0,
      size = 150,
      color='#fec02f',  
      label='Number of Scans',
      style={'color':'#fec02f'},
      showCurrentValue=True,
      labelPosition='top')
# ==========================================================
# T A B 1 - L A Y O U T 
# ==========================================================
# TODO: IMPROVE TOOLTIPS
tab1_Layout = dbc.Container(fluid=True,children=[
    dbc.Row([
        dbc.Col(html.Center(region_name),width = {'size':4,'offset':0},align='center'),
        dbc.Col([
                html.Center(brain_cockpit)],align='center', width = {'size':3,'offset':0}),
        dbc.Col(html.Center(guage_brain),align='center',width = {'size':4,'offset':0})
        ],justify="center"),
    dbc.Row([
        dbc.Col([html.Br(),
                 html.Center(vendor_brain_t1),
                 html.Br(),
                 dbc.Row([
                 html.Center(led_tesla_brain),
                 html.Center(led_avg_brain),
                 html.Center(led_std_brain)],justify='around'),
        ],width=10)
    ],justify="center"),
    dbc.Tooltip(
        "Certain ROIs were not possible to be placed on some scans due to slice prescriptions.",
        target="guage-brain",
        placement = "top"  
    ),
    dbc.Tooltip(
        "Select a vendor to update values.",
        target="vendor-slider",
        placement = 'top'
    ),
])

# =========================================================================


@app.callback([Output(component_id='region-name', component_property='children'),
               Output('led-avg-brain','value'),
               Output('led-std-brain','value'),
               Output('guage-brain','value')
               ],
              [Input(component_id='fig-brain', component_property='clickData'),
              Input('vendor-slider','value'),
              Input('session-id', 'children')
              ])
def update_output1(hoverData,vendor,session_id):
    df = get_dataframe_brain(session_id)
    if hoverData is not None:
        if (hoverData['points'][0]['y'],hoverData['points'][0]['x']) in rrsg_brain.keys():
            region = rrsg_brain[(hoverData['points'][0]['y'],hoverData['points'][0]['x'])]
            if region != 'Ventricles':
                if vendor == 1: 
                    tmp = df[df['MRI vendor']=='Siemens']
                elif vendor == 2: 
                    tmp = df[df['MRI vendor']=='GE'] 
                elif vendor == 3:
                    tmp = df[df['MRI vendor']=='Philips']
                else:
                    tmp=df
                tmp = np.array(tmp[region])
                avg = []
                std = []
                for ii in tmp:
                    if ii: 
                        avg.append(np.mean(ii))
                        std.append(np.std(ii))
                num = len(avg)
                avg = np.round(np.mean(avg))
                std = np.round(np.mean(std))
            else:
                avg = 0
                std = 0
                num=0
        else:
            region = 'N/A'
            avg = 0
            std = 0
            num = 0
    else:
        region = 'Click on a region'
        avg = 0
        std = 0
        num = 0
    return  html.H5('     ' + region,style={'color':'#fec02f'}),avg,std,num


# Y-AXIS FIX/RELEASE| TAB2 | toggle-axis
toggle_ax_br = daq.BooleanSwitch(
    label='Fix/Release y-Axis',
    labelPosition='bottom',
    id = 'toggle-axis'
)

# T A B 2 - L A Y O U T 
# ==========================================================                             
tab2_Layout = dbc.Container(fluid=True,children=[
    dbc.Row([
        dbc.Col([html.Center(brain_cockpit),
                html.Br(),
                html.Center(vendor_brain_t1),
                html.Br(),
                html.Center(toggle_ax_br)],width={"size":4,"offset":0},align="center")])
#        dbc.Col([boxes,
#                 dbc.Row([dbc.Col([html.Center(vendor_lbl)],align="center"),
#                          dbc.Col([led_sphere],align="center"),
#                          dbc.Col([html.Center(site_t2)],align="center")
#                ],justify="center")
#        ],width={"size":8,"offset":0},align="center")]),  
        ])
