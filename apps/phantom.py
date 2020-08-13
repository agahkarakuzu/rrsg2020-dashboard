import numpy as np
import matplotlib.pyplot as plt
import math
import plotly.graph_objects as go
import pandas as pd
import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import dash_daq as daq
import dash_bootstrap_components as dbc
from app import app, get_dataframe
from apps import home
import os

# ==========================================================
# N I S T - R E F E R E N C E  V A L U E S
# ==========================================================
NIST_REF = dict()
NIST_REF.update({"V1":{"Mean":[1989,1454,984.1,706,496.7,351.5,247.13,175.3,125.9,89,62.7,44.53,30.84,21.71],
                       "Median":[1989,1454,984.1,706,496.7,351.5,247.13,175.3,125.9,89,62.7,44.53,30.84,21.71],
                      "STD":[1,2.5,0.33,1.5,0.41,0.91,0.086,0.11,0.33,0.17,0.13,0.09,0.016,0.005  ]}})
NIST_REF.update({"V2":{"Mean":[1833.97,1330.16,987.27,690.08,484.97,341.58,240.86,174.95,121.08,85.75,60.21,42.89,30.40,21.44],
                       "Median":[1833.97,1330.16,987.27,690.08,484.97,341.58,240.86,174.95,121.08,85.75,60.21,42.89,30.40,21.44],
                      "STD":[30.32,20.41,14.22,10.12,7.06,4.97,3.51,2.48,1.75,1.24,0.87,0.44,0.62,0.31]}})

def circle_points(r, n):
    circles = []
    for ii in range(n):
        x =  r * np.cos(2 * math.pi * ii/ n)
        y =  r * np.sin(2 * math.pi * ii/ n)
        circles.append([x, y])
    return circles

def rotate_spheres(circles,radians):
    rotated = []
    for ii in range(len(circles)):   
        x =  circles[ii][0] * math.cos(radians) + circles[ii][1] * math.sin(radians)
        y = -circles[ii][0] * math.sin(radians) + circles[ii][1] * math.cos(radians)
        rotated.append([x,y])
    return rotated

def nist_figure(t1,phan_name,radius,scaleshow,show_logos,SN,unit,showtype):
    # Draw 10 outer spheres
    circles_out = circle_points(radius/1.3, 10)
    # -90deg rotation to match indexing order & phantom design
    circles_out = rotate_spheres(circles_out,np.deg2rad(-90))
    # Draw 4 inner spheres
    circles_in = circle_points(radius/2.16, 4)
    # -45deg rotation to match indexing order & phantom design
    circles_in = rotate_spheres(circles_in,np.deg2rad(-45))
    # Merge 
    circles = circles_out + circles_in
    # Create figure
    fig = go.Figure()
    ply_shapes = {}
    ply_shapes.update({'plate' : go.layout.Shape(
                type="circle",
                x0=-radius,
                y0=-radius,
                x1=radius,
                y1=radius,
                fillcolor="#7E7F9A",
                layer="below",
                opacity=0.5,
                line_width=3,
                line_color='darkgray')})    
    ply_shapes.update({'rect' : go.layout.Shape(
                type="rect",
                x0=-radius/2.95,
                y0=-radius/6.5,
                x1=radius/2.95,
                y1=radius/6.5,
                fillcolor="lightgray",
                layer="below",
                opacity=0.3,
                line_width=0)})    
    if radius<=4 or (radius>=7 and radius<9):
        scale = radius/6.5
    else:
        scale = 1
    for ii in range(len(circles)):
            if unit == '%':
                add_text = ' difference from the'
            else:
                add_text = ''

            if SN == 'V1':
                hovertext = '<b>Sphere ' + str(ii+1) + '</b>' + '<br>'+str(np.round(t1[ii],2)) + ' ' + unit + add_text + '<br> target: ' + str(np.round(NIST_REF['V1']['Mean'][ii])) + '&plusmn;' + str(np.round(NIST_REF['V1']['STD'][ii])) + ' ms'                
            elif SN == 'V2':
                hovertext = '<b>Sphere ' + str(ii+1) + '</b>' + '<br>'+str(np.round(t1[ii],2)) + ' ' + unit + add_text + '<br> target: ' + str(np.round(NIST_REF['V2']['Mean'][ii])) + '&plusmn;' + str(np.round(NIST_REF['V2']['STD'][ii])) + ' ms'
            else:
                hovertext = '<b>Sphere ' + str(ii+1) + '</b>' + '<br>'+str(np.round(t1[ii],2)) + ' ' + unit
            
            if (SN != 'V1') & (SN != 'V2') & (SN != 'N/A'):
                if int(SN) < 42:
                    hovertext = '<b>Sphere ' + str(ii+1) + '</b>' + '<br>'+str(np.round(t1[ii],2)) + ' ' + unit + add_text + '<br> target: ' + str(np.round(NIST_REF['V1']['Mean'][ii])) + '&plusmn;' + str(np.round(NIST_REF['V1']['STD'][ii])) + ' ms'                
                elif int(SN) > 41:
                    hovertext = '<b>Sphere ' + str(ii+1) + '</b>' + '<br>'+str(np.round(t1[ii],2)) + ' ' + unit + add_text + '<br> target: ' + str(np.round(NIST_REF['V2']['Mean'][ii])) + '&plusmn;' + str(np.round(NIST_REF['V2']['STD'][ii])) + ' ms'
                else: 
                    hovertext = '<b>Sphere ' + str(ii+1) + '</b>' + '<br>'+str(np.round(t1[ii],2)) + ' ' + unit
            if (SN=='N/A'):
                hovertext = '<b>Sphere ' + str(ii+1) + '</b>' + '<br>'+str(np.round(t1[ii],2)) + ' ' + unit

            fig.add_trace(go.Scatter(
            x=[circles[ii][0]],
            y=[circles[ii][1]], 
            hoverinfo= 'text',    
            mode="markers",
            marker = dict(color=[t1[ii]],
                          size=45*(radius/6.5*scale),
                          colorscale="viridis",
                          line=dict(color="darkgray",width=4*(radius/6.5*scale)),
                          cmin = np.min(t1),
                          cmax = np.max(t1), 
                          colorbar=dict(len=0.8,ticks="inside",thickness=10,tickcolor="white",tickfont=dict(color="white",size=10),title=dict(text=unit,font=dict(color="white"),side="bottom"),dtick=np.max(t1)/6,nticks=7,xanchor = "left", x=-0.06),
                          showscale=scaleshow
                         ), 
            name = 'Sphere ' + str(ii+1),  
            hovertext = hovertext
            ))
    if showtype == 'values':
        annotations = [{'x':circles[ii][0],'y':circles[ii][1],'text':str(np.round(t1[ii],1)),'showarrow':False,'font': {'color':'white'}} for ii in range(len(circles))]
        fig.update_layout(annotations=annotations)
    
    lst_shapes=list(ply_shapes.values())
    
    fig.add_annotation(
        x=0,
        y=0,
        text="<b>"+ phan_name + "</b>",
        showarrow=False,
        font=dict(
            family="Courier New, monospace",
            size=12*(radius/6.5),
            color="black"
            ),
        align="center"
        )
    
    fig.add_annotation(
    x=(circles[12][0]+circles[13][0])/2-0.1,
    y=circles[12][1],
    text="<b> SN:"+ str(SN) + "</b>",
    showarrow=False,
    font=dict(
        family="Courier New, monospace",
        size=12*(radius/6.5),
        color="black"
        ),
    align="center"
    )
        
    if show_logos:
        logo_size = 1.8*(radius/6.5)
        fig.add_layout_image(
        dict(
            source="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/NIST_logo.svg/645px-NIST_logo.svg.png",
            xref="x", yref="y",
            x=logo_size/2, y=circles[11][1],
            sizex=logo_size, sizey=logo_size,
            xanchor="right", yanchor="bottom"
        ))
        fig.add_layout_image(
        dict(
            source="data:image/png;base64,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",
            xref="x", yref="y",
            x=logo_size/2*1.2, y=circles[11][1]-0.1,
            sizex=logo_size*1.2, sizey=logo_size*1.2,
            xanchor="right", yanchor="top"
        ))
    fig.update_layout(clickmode="event")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    if scaleshow:
        wdth = 420
    else:
        wdth = 400
    fig.update_layout(width=wdth*(radius/6.5),height=400*(radius/6.5),shapes=lst_shapes,plot_bgcolor="#060606",paper_bgcolor="#060606",showlegend=False)
    fig.update_layout(yaxis=dict( range=[-1.2*radius, 1.2*radius],showgrid=False, zeroline=False, showticklabels=False ))
    fig.update_layout(xaxis=dict( range=[-1.2*radius, 1.2*radius],showgrid=False, zeroline=False,showticklabels=False  ))
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return fig

def llincc(x,y):
    """
Calculates Lin's concordance correlation coefficient.
Usage:   alincc(x,y)    where x, y are equal-length arrays
Returns: Lin's CC
"""
    covar = lcov(x,y)*(len(x)-1)/float(len(x))  # correct denom to n
    xvar = lvar(x)*(len(x)-1)/float(len(x))  # correct denom to n
    yvar = lvar(y)*(len(y)-1)/float(len(y))  # correct denom to n
    lincc = (2 * covar) / ((xvar+yvar) +((amean(x)-amean(y))**2))
    return lincc

def calculate_concordance(xydata):
    """Created march 2003 by G.W.Payne
       Concordance calculator as described by Mr Graham McBride.
    """
    n = 0  #number pairs
    SumX = float(0)  #sum of X values
    SumY = float(0)  #sum of Y values
    SumXX = float(0)  #sum of squares of x values
    SumYY = float(0)  #sum of squares of x values
    VarX = float(0)  #variance of X values
    VarY = float(0)  #variance of Y
    MeanX = float(0)  #Mean of X values
    MeanY = float(0)  #Mean of Y values
    #SQR_MeanX=float(0)              #MeanX squared
    #SQR_MeanY=float(0)              #Mean of Y squared
    SumCoVarXY = float(0)  #Sum of CoVariance of X,Y pairs
    CoVarXY = float(0)  #CoVariance of X,Y pairs
    Lins_rc = float(0)  #Sample Concordance corerelation coefficient (Lins rc)
    #calculate sums and sums of squares
    for point in xydata:
        n = n + 1
        SumX = SumX + (point[0])
        SumY = SumY + (point[1])
        SumXX = SumXX + (point[0])**2
        SumYY = SumYY + (point[1])**2
    #calculate means
    MeanX = SumX / n
    MeanY = SumY / n
    #calculate Square roots of Means
    #SQR_MeanX=math.sqrt(MeanX)
    #SQR_MeanY=math.sqrt(MeanY)
    #calculate variance for X and Y's
    VarX = (n * SumXX - SumX**2) / n**2
    VarY = (n * SumYY - SumY**2) / n**2
    #calculate Covariance of X,Y pairs
    for point in xydata:
        SumCoVarXY = SumCoVarXY + ((point[0]) - MeanX) * ((point[1]) - MeanY)
    CoVarXY = SumCoVarXY / n
    #calculate Lins concordance
    Lins_rc = 2 * CoVarXY / (VarX + VarY + (MeanX - MeanY)**2)
    return round(Lins_rc,5)

    # TODO: Arrange for deployment
#cache = Cache(app.server, config={
#    'CACHE_TYPE': 'redis',
    # Note that filesystem cache doesn't work on systems with ephemeral
    # filesystems like Heroku.
#    'CACHE_TYPE': 'filesystem',
#    'CACHE_DIR': 'cache-directory',

    # should be equal to maximum number of users on the app at a single time
    # higher numbers will store more data in the filesystem / redis cache
#    'CACHE_THRESHOLD': 2
#})

#def get_dataframe(session_id):
#    @cache.memoize()
#    def query_and_serialize_data(session_id):
        
#        phan_df = pd.read_pickle('3T_NIST_T1maps_database.pkl')

#        return phan_df.to_json()

#    return pd.read_json(query_and_serialize_data(session_id))


# Dash DAQ dark theme wrapper theme colors
theme =  {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E'
}

# Vendor logos scraped from the web 
siemens_logo = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Siemens_Healthineers_logo.svg/1280px-Siemens_Healthineers_logo.svg.png"
ge_logo = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/General_Electric_logo.svg/768px-General_Electric_logo.svg.png"
philips_logo = "https://2.bp.blogspot.com/-vasS5YTdDB0/UoN_LZjqlUI/AAAAAAAAcqo/gYjlvFx0CBg/s1600/Philips+shield.png"

# Create an empty figure that is coherent with the theme
empty_figure = go.Figure(layout={
  'plot_bgcolor':"#060606",
  'paper_bgcolor':"#060606",
  "xaxis":{"showgrid":False,"zeroline":False,"showticklabels":False},
  "yaxis":{"showgrid":False,"zeroline":False,"showticklabels":False}})

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| TAB 1 CONTENT
# =================================================================================
#   ______      __         ___
#  /_  __/___ _/ /_       <  /
#   / / / __ `/ __ \______/ / 
#  / / / /_/ / /_/ /_____/ /  
# /_/  \__,_/_.___/     /_/ 

# DCC that will contain phantom 
nist_cockpit = dcc.Graph(
        id='phantom-figure',
        figure=empty_figure,
         config={
        'displayModeBar': False    
        })

# The gauge to show # of scans (after selection)
guage = daq.Gauge(
      id='guage-scans',
      min=0,
      max=40,
      value=6,
      size = 150,
      color='lightgreen',  
      label='Number of Scans',
      style={'color':'#ADAFAE'},
      showCurrentValue=True,
      labelPosition='top')

# THERMOMETER | TAB1 | thermo-avg
thermo = daq.Thermometer(
        id = "thermo-avg",
        scale={'start': 12, 'interval': 2,
            'labelInterval': 4, 'custom': {
                '20': '(Ref) 20'
            }},
        max = 35,
        value=20,
        width=5,
        height=100,
        label = "Avg Temp (C)",
        showCurrentValue=True,
        style={'color':'#ADAFAE'},
        labelPosition='top',
        theme='dark')


# TOGGLE TESLA | TAB1 | toggle-tesla
toggle_tesla = daq.BooleanSwitch(
    label='Field Strength',
    labelPosition='bottom',
    id = 'toggle-tesla'
)

# TLED TESLA | TAB1 | led-tesla
led_tesla = daq.LEDDisplay(
    label="Field Strength (T)",
    value='3.00',
    color="lightgreen",
    id = 'led-tesla'
)  

# TOGGLE SERIAL NUMBER| TAB1 | toggle-SN
toggle_SN = daq.BooleanSwitch(
    label='Phantom Version',
    labelPosition='bottom',
    id = 'toggle-SN'
)

# LED SN | TAB1 | led-SN
led_SN = daq.LEDDisplay(
    label="Phantom SN | From:To",
    value='0:0',
    color="lightgreen",
    id='led-SN'
)  



# VENDOR DROPDOWN | TAB1 | vendor-dropdown-t2
vendor_list = dcc.Dropdown(
    options=[
        {'label':'All vendors','value':'All'},
        {'label': 'Siemens', 'value': 'Siemens'},
        {'label': 'GE', 'value': 'GE'},
        {'label': 'Philips', 'value': 'Philips'}
    ],
    value='All',
    multi=False,
    id = "vendor-dropdown-t1",
    placeholder = 'Select vendor(s)'
)


# VENDOR LOGOS | TAB1 | vendor-logo
# IMPORTANT Value of this div is checked to infer which vendor is selected 
vendor_logo = html.Div(children=[],id='vendor-logo')

# DROPDOWN METRIC ================================================
# This will update a hidden div. This is a compromise I made to make UI
# elements share CYBORG theme.. To be improved later. 

#items_metric = [
#    dbc.DropdownMenuItem("Mean",id="dropdown-mean"),
#    dbc.DropdownMenuItem(divider=True),
#   dbc.DropdownMenuItem("STD",id="dropdown-std"),
#    dbc.DropdownMenuItem(divider=True),
#    dbc.DropdownMenuItem("Median",id="dropdown-median"),
#    dbc.DropdownMenuItem(divider=True),
#    dbc.DropdownMenuItem("CoV",id="dropdown-cov")]

#metric_list = dbc.DropdownMenu(label="Display Metric", children=items_metric, direction="left", id="dropdown-metric")

# VENDOR DROPDOWN | TAB1 | vendor-dropdown-t2
metric_list = dcc.Dropdown(
    options=[
        {'label':'Mean','value':'Mean'},
        {'label': 'STD', 'value': 'STD'},
        {'label': 'Median', 'value': 'Median'},
        {'label': 'CoV', 'value': 'CoV'}
    ],
    multi=False,
    value = 'Mean',
    id = "metric-dropdown-t1",
    placeholder = 'Select a metric'
)


# ==========================================================
# T A B 1 - C A L L B A C K S
# ==========================================================
# CALLBACK: UPDATE VENDOR LOGO @DROPDOWN VENDOR +++++++++++++++++++++++++++++
@app.callback([Output(component_id='metric-label',component_property='children'),
               Output(component_id='toggle-deviation',component_property='disabled'),
               Output(component_id='toggle-deviation',component_property='on'),
              ],
             [Input(component_id='metric-dropdown-t1',component_property="value")])
def update_metric_label(inp):
    if inp=='Mean':
        return [html.H5('Mean',style={"color":"lightgreen"}), False,False]
    elif inp=='STD':
        return [html.H5('STD',style={"color":"lightgreen"}), False,False]
    elif inp=='Median':
        return [html.H5('Median',style={"color":"lightgreen"}), False,False]
    elif inp=='CoV':
        return [html.H5('CoV',style={"color":"lightgreen"}), True,False]
    else: 
        return [html.H5('Mean',style={"color":"lightgreen"}), False,True]
    
# DEVIATION ==========================================================
# Only active when dropdown metric == mean or STD
# TOGGLE DEVIATION | TAB1 | toggle-deviation
toggle_deviation = daq.BooleanSwitch(
    label='% Difference from target',
    labelPosition='bottom',
    id = 'toggle-deviation'
)

# ==========================================================
# T A B 1 - L A Y O U T 
# ==========================================================
# TODO: IMPROVE TOOLTIPS
tab1_Layout = dbc.Container(fluid=True,children=[
    dbc.Row([
        dbc.Col([ html.Br(),
                html.Center(vendor_list),
                html.Br(),
                html.Center(toggle_tesla),
                html.Br(),html.Center(toggle_SN)],width={"size":3,"offset":0},align="center"),
        dbc.Col([html.Center(html.Div(id="metric-label",children=[])),
                 html.Center(html.Div(id="submit",children=[])),
                nist_cockpit],
                width={"size":5,"offset":0},align="center"),
        dbc.Col([html.Center(metric_list),
                html.Br(),
                html.Center(toggle_deviation),
                ],width={"size":3,"offset":0},align="center")
        ],justify="around"),
    dbc.Row([
        dbc.Col(led_tesla,width=2,align="center"),
        dbc.Col(led_SN,width=2,align="center"),
        dbc.Col(thermo,width=2,align="center"),
        dbc.Col(vendor_logo,width=2,align="center"),
        dbc.Col(guage,width=2,align="center")
    ],justify="center"),
      dbc.Tooltip(
        "Toggle between 0.35T and 3T. Only enabled for Siemens.",
        target="toggle-tesla",
        placement = "right"  
    ),
      dbc.Tooltip(
        "Reference values of ISMRM/NIST phantoms "
        "after SN 42 are different.",  
        target="toggle-SN",
        placement = "right"  
    )
#    dbc.Tooltip(
#        "Select a vendor",  
#        target="dropdown-vendor",
#        placement = "top"  
#    ),
#        dbc.Tooltip(
#        "Click this button to update "
#        "phantom values with respect to your selections.",
#        target="submit",
#        style={"color":"black","background-color":"#26a96c"},    
#        placement = "top"  
#    )
])
# =========================================================================

# STYLE TABS 
tab_style = {"background-color":"#26a96c",
             "margin-left":"2px",
             "border-radius": "5px 5px 0px 0px",
             "cursor":"grab"}

tab_style_home = {"background-color":"#e84855",
                  "margin-left":"2px",
                  "border-radius": "5px 5px 0px 0px",
                  "cursor":"grab"}

# Associate layouts with tabs 
#rootLayout = dbc.Tabs(
#             [
#                 dbc.Tab([],label="Big Picture",tab_id="big-picture",tab_style=tab_style,label_style={"color": "white"}),
#                 dbc.Tab(label="By Sphere",tab_id="anan2",tab_style=tab_style,label_style={"color": "white"}),
#                 dbc.Tab(label="By Site",tab_id="anan",tab_style=tab_style,label_style={"color": "white"}),
#                 dbc.Tab(label="Home",tab_id="home", tab_style=tab_style_home,label_style={"color": "white"})
#             ], 
#            id = "tabs",
#            active_tab="big-picture"
#             )



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
            [
                 dbc.Tab(label = 'Home',tab_id="home", tab_style=tab_style_home,label_style={"color": "white"}),
                 dbc.Tab(label="Big Picture",tab_id="big-picture",tab_style=tab_style,label_style={"color": "white"}),
                 dbc.Tab(label="By Sphere",tab_id="by-sphere",tab_style=tab_style,label_style={"color": "white"}),
                 dbc.Tab(label="By Site",tab_id="by-site",tab_style=tab_style,label_style={"color": "white"}),
            ],
            id="tabs-phantom",
            active_tab="big-picture",
        ),
        html.Div(id="content"),
    ],
    style = {'height':'90vh'}
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

# CONSTRUCTOR FOR SERVE LAYOUT 
# ****************************
#layout = serve_layout
# ****************************   

# M A I N - T A B  S W I T C H  C A L L B A C K --------------------------
# =========================================================================
@app.callback([Output("content", "children"),Output('tabs-phantom','style')], [Input("tabs-phantom", "active_tab"),Input('session-id', 'children')])
def switch_tab(at,session_id):
    if at == "big-picture":
        df = get_dataframe(session_id)
        df = df.round(2) # Set precision 
        return [tab1_Layout,{'visibility':'visible'}]
    elif at == "by-sphere":
        return [tab2_Layout,{'visibility':'visible'}]
    elif at == "by-site":
        return [tab3_Layout,{'visibility':'visible'}]
    elif at == 'home':
        return [home.layout,{'visibility':'hidden','height':'0px'}]
    

# ==========================================================
# T A B 1 - C A L L B A C K S | CONT'D 
# ==========================================================
# CALLBACK: UPDATE VENDOR LOGO @DROPDOWN VENDOR +++++++++++++++++++++++++++++
@app.callback([Output(component_id='vendor-logo',component_property='children'),
               Output(component_id='toggle-tesla',component_property='disabled'),
               Output(component_id='led-tesla',component_property='value'),
               Output(component_id='toggle-SN',component_property='on'),
               Output(component_id='toggle-SN',component_property='disabled')
             ],
             [Input(component_id='vendor-dropdown-t1',component_property="value"),
             Input(component_id='toggle-tesla',component_property="on")
             ])
def update_vendor_logo(inp,val):
    if inp=='All':
        return html.H4('All vendors',style={"color":"lightgreen"}), True, '3.00',False, False
    elif inp=='Siemens':
        if val:
            return html.Img(src=siemens_logo,style={"width":"200px"}), False, '0.35',True, True
        else:
            return html.Img(src=siemens_logo,style={"width":"200px"}), False, '3.00',False, False  
    elif inp=='GE':
        return html.Img(src=ge_logo,style={"width":"100px"}), True,'3.00',False, False  
    elif inp=='Philips':
        return html.Img(src=philips_logo,style={"width":"100px"}), True,'3.00',False, False  
    else:
        return html.H4('All vendors',style={"color":"lightgreen"}), True,'3.00',False, False  

# CALLBACK: UPDATE TESLA TOGGLE @DROPDOWN VENDOR +++++++++++++++++++++++++++++
#@app.callback([Output(component_id='toggle-tesla',component_property='disabled'),
#               Output(component_id='toggle-tesla',component_property="on")
#              ],
#             [Input(component_id='dropdown-sie',component_property="n_clicks"),
#              Input(component_id='dropdown-phi',component_property="n_clicks"),
#              Input(component_id='dropdown-all',component_property="n_clicks"),
#              Input(component_id='dropdown-ge',component_property="n_clicks")])
#def update_tesla_state(btn1,btn2,btn3,btn4):
#    ctx = dash.callback_context
#    if ctx.triggered[0]['prop_id'].split('.')[0] == "dropdown-sie":
#        return False, False
#    else:
#        return True, False

# CALLBACK: UPDATE TESLA LED & SN TOGGLE @DROPDOWN VENDOR & TOGGLE TESLA +++++++
#@app.callback([Output(component_id='led-tesla',component_property='value'),
#               Output(component_id='toggle-SN',component_property='on'),
#               Output(component_id='toggle-SN',component_property='disabled'),
#              ],
#             [Input(component_id='toggle-tesla',component_property="on"),
#              Input(component_id='dropdown-sie',component_property="n_clicks"),
#              Input(component_id='dropdown-phi',component_property="n_clicks"),
#              Input(component_id='dropdown-all',component_property="n_clicks"),
#              Input(component_id='dropdown-ge',component_property="n_clicks")])
#def update_tesla_led(val,btn1,btn2,btn3,btn4):
#    # val is the value of toggle tesla
#    ctx = dash.callback_context
#    if ctx.triggered[0]['prop_id'].split('.')[0] == "toggle-tesla":
#        if val:
#            return '0.35',True, True
#        else:
#            return '3.00',False, False
#    else:
#        return '3.00',False, False

def get_t1_arr(inp,metric,version,deviation):
    """
    np.ndarray --> list for multiple phantoms upon 
    a selected metric, possible to calculate % dif 
    based on reference Mean and STD vals provided 
    by NIST (phantom ver dependent)
    """
    t1 = []
    inp = np.array(inp)
    if metric == "CoV":
        unit = 'a.u.'
    else:
        unit = 'ms'
    for ii in range(len(inp)):
        cur = []
        num = len(np.array(inp[ii]))
        if num>0 and list(inp[ii]) != None:
            for jj in range(num):
                if inp[ii][jj] != None:
                    if metric == "Mean":
                        cur.append(np.mean(inp[ii][jj]))
                    if metric == "Median":    
                        cur.append(np.median(inp[ii][jj]))
                    if metric == "STD":
                        cur.append(np.std(inp[ii][jj]))
                    if metric == "CoV":
                        cur.append(np.std(inp[ii][jj])/np.mean(inp[ii][jj]))
                   
                    
            # This should be mean either way (dashboard shows mean STD, mean COV etc.)        
            t1.append(np.mean(cur))    
        else:
            t1.append(0)
            
    if deviation:
        t1 = list(np.abs(np.array(t1) - np.array(NIST_REF[version][metric]))/(np.array(NIST_REF[version][metric]))*100) 
        unit = "%"
    return t1,num,unit

def slice_phan_data_t1(df,vendor,metric,tesla,lower,upper,version,deviation):
    """
    Helper function to slice data. 
    """
    df = df.round(2) # So that we can find 0.35
    NIST_SPHERES = ['T1 - NIST sphere ' + str(ii+1) for ii in range(14)]
    if vendor == "All":
        cond = ((df['MRI field']==float(tesla)) &         
            (df['phantom serial number'] > lower) & 
            (df['phantom serial number'] < upper))
    else:
        cond = ((df['MRI field']==float(tesla)) & 
            (df['MRI vendor'] == vendor) &          
            (df['phantom serial number'] > lower) & 
            (df['phantom serial number'] <= upper))   
    slc = [df[cond][sph] for sph in NIST_SPHERES ]
    tmp = np.mean(list(df[cond]['phantom temperature']))
    if np.isnan(tmp):
        tmp = 0
    t1,num,unit = get_t1_arr(slc,metric,version,deviation)
    
    return t1, tmp, num, unit
   
# CALLBACK: UPDATE SN LED @SN TOGGLE +++++++++++++++++++++++++++++++++
@app.callback(Output(component_id='led-SN',component_property='value'),
             [Input(component_id='toggle-SN',component_property="on")])
def update_phantom_led(val):
    if not val:
        return '0:41'
    else:
        return '42:102'

NIST_SPHERES = [['T1 - NIST sphere ' + str(ii+1)] for ii in range(14)]
# CALLBACK: UPDATE NIST COCKPIT +++++++++++++++++++++++++++++++++
@app.callback([Output(component_id='phantom-figure',component_property='figure'),
               Output(component_id='guage-scans',component_property='value'),
               Output(component_id='thermo-avg',component_property='value'),
               Output('submit','children')
              ],
             [Input('session-id', 'children'),
              Input(component_id='led-tesla',component_property="value"),
              Input(component_id='led-SN',component_property="value"),
              Input(component_id='vendor-logo',component_property="children"),
              Input(component_id='metric-label',component_property="children"),
              Input(component_id='toggle-deviation',component_property="on")
             ]
             )
def update_phantom(session_id,tesla,SN,vendor,metric,deviation):
    """
    Helper function for TAB 1 
    """
    # Get cached data 
    df = get_dataframe(session_id)
    #print(session_id)
    if deviation: 
        dev_msg = html.H6('Percent difference',style={'color':'skyblue'})
    else:
        dev_msg = html.H6('Summary stats',style={'color':'skyblue'})

    if not metric == None:
        if SN == "0:41":
            lower =0
            upper = 41
            version = "V1"
        else:
            lower = 41
            upper = 103 # TODO: CHANGE THIS WHEN THE DF IS COMLETE
            version = "V2"
        
        if vendor['props']['children'] == "All vendors":
            vndr = "All"
        else:
            if vendor['props']['src'] == siemens_logo:
                vndr = "Siemens"
            elif vendor['props']['src'] == philips_logo:
                vndr = "Philips"
            elif vendor['props']['src'] == ge_logo:
                vndr = "GE"      

        metric = metric['props']['children']        
        t1,tmp,num,unit = slice_phan_data_t1(df,vndr,metric,tesla,lower,upper,version,deviation)

        return nist_figure(t1,'Hover spheres <br> T1 Plate',7,True,True,version,unit,'values'), num, tmp, dev_msg
    else:
        t1,tmp,num, unit = slice_phan_data_t1(df,"All","Mean",3.00,0,41,"V1",False)
        return nist_figure(t1,'Hover spheres <br> T1 Plate',7,True,True,'V1',unit,'values'), num, tmp, dev_msg


# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| TAB 2 CONTENT
# =========================================================================
#  ______      __         ___ 
# /_  __/___ _/ /_       |__ \
#  / / / __ `/ __ \________/ /
# / / / /_/ / /_/ /_____/ __/ 
#/_/  \__,_/_.___/     /____/ 
                             

# FIXME: FIX UPPER & LOWER LIMITS 
def slice_phan_data_t2(df,SN,vendor,sph):
    df = df.round(2) # So that we ccoan find 0.35
    dat = []
    for vd in vendor: 
        dat.append(df[df['MRI vendor']==vd])
    tmp_df = pd.concat(dat)   
    # Get 3T data only
    tmp_df = tmp_df[tmp_df['MRI field']==3.00]
    
    if len(SN)==1 and SN[0]=="V1":
        tmp_df = tmp_df[(tmp_df['phantom serial number']>0) & (tmp_df['phantom serial number']<41)]
        ret = [tmp_df['site name'],np.array(tmp_df['T1 - NIST sphere ' + str(sph)]),tmp_df['MRI vendor']]    
    elif len(SN)==1 and SN[0]=="V2":    
        tmp_df = tmp_df[(tmp_df['phantom serial number']>41) & (tmp_df['phantom serial number']<103)]
        ret = [tmp_df['site name'],np.array(tmp_df['T1 - NIST sphere ' + str(sph)]),tmp_df['MRI vendor']]
    elif len(SN)==2:
        ret = [tmp_df['site name'],np.array(tmp_df['T1 - NIST sphere ' + str(sph)]),tmp_df['MRI vendor']]
    elif len(SN)==0:
        ret = [[],[],[]]
    return ret 

# VENDOR DROPDOWN | TAB2 | vendor-dropdown-t2
vendor_t2 = dcc.Dropdown(
    options=[
        {'label': 'Siemens', 'value': 'Siemens'},
        {'label': 'GE', 'value': 'GE'},
        {'label': 'Philips', 'value': 'Philips'}
    ],
    value=['Siemens', 'GE','Philips'],
    multi=True,
    id = "vendor-dropdown-t2",
    placeholder = 'Select vendor(s)'
)

# SN DROPDOWN | TAB2 | SN-dropdown-t2
SN_t2 = dcc.Dropdown(
    options=[
        {'label': 'SN 0:41', 'value': 'V1'},
        {'label': 'SN 42:103', 'value': 'V2'}
    ],
    value=['V1'],
    multi=True,
    placeholder="Select phantom version(s)",
    id = "SN-dropdown-t2"
)  

# PHANTOM FIGURE | TAB2 | phantom-selector
nist_cockpit2 = dcc.Graph(
        id='phantom-selector',
        figure=nist_figure(NIST_REF['V1']['Mean'],'<b>HOVER SPHERES</b>',7,False,True,0,"ms",'values'),
         config={
        'displayModeBar': False    
        })

# SPHERE-WISE BOXPLOTS| TAB2 | sphere-boxes
boxes = dcc.Graph(
        id='sphere-boxes',
        figure=empty_figure,
         config={
        'displayModeBar': True    
        })

# Y-AXIS FIX/RELEASE| TAB2 | toggle-axis
toggle_ax = daq.BooleanSwitch(
    label='Fix/Release y-Axis',
    labelPosition='bottom',
    id = 'toggle-axis'
)

# SELECTED SPHERE LED | TAB2 | led-sphere
led_sphere = daq.LEDDisplay(
    label="Selected Sphere",
    value='1.00',
    color="lightgreen",
    id = 'led-sphere'
)  

# VENDOR LOGO | TAB2 | vendor-t2
vendor_lbl = html.Div(
  id="vendor-t2",
  children=[
   html.Img(
    src=siemens_logo,
    style={"width":"200px"})])

# SITE NAME| TAB2 | cur_site
site_t2 = html.Div(id="cur_site",
  children=[
   html.H5('This is the center')])

# ==========================================================
# T A B 2 - L A Y O U T 
# ==========================================================                             
tab2_Layout = dbc.Container(fluid=True,children=[
    dbc.Row([
        dbc.Col([html.Center(nist_cockpit2),
                html.Br(),
                html.Center(SN_t2),
                html.Br(),
                html.Center(vendor_t2),
                html.Br(),
                html.Center(toggle_ax)],width={"size":4,"offset":0},align="center"),
        dbc.Col([boxes,
                 dbc.Row([dbc.Col([html.Center(vendor_lbl)],align="center"),
                          dbc.Col([led_sphere],align="center"),
                          dbc.Col([html.Center(site_t2)],align="center")
                ],justify="center")
        ],width={"size":8,"offset":0},align="center"),]),
        dbc.Tooltip(
            "Dashed lines indicate reference values. Yellow: V1 and Red: V2.",
             target='sphere-boxes',
             placement= 'top'),  
        ],style={'height':'90vh'})

# ==========================================================
# T A B 2 - C A L L B A C K S
# ==========================================================
@app.callback([Output(component_id='sphere-boxes',component_property='figure'),
               Output("led-sphere","value")],
             [Input(component_id='phantom-selector',component_property="hoverData"),
              Input('session-id', 'children'),Input('toggle-axis', 'on'),
              Input(component_id='SN-dropdown-t2',component_property="value"),
              Input(component_id='vendor-dropdown-t2',component_property="value")
             ])
def update_boxplots(sph,session_id,axs,SN,vendor):
    df = get_dataframe(session_id)
    if sph != None:
        
        selected = sph['points'][0]['curveNumber']+1
        ref1 = NIST_REF['V1']['Mean'][selected-1]
        ref2 = NIST_REF['V2']['Mean'][selected-1]
        aa, bb,cc = slice_phan_data_t2(df,SN,vendor,selected)
        figb = go.Figure()
        if not len(bb) == 0:
            for b in range(len(bb)):
                if bb[b] != None:
                    figb.add_trace(go.Box(y=list(bb[b]),
                                boxpoints='all', # can also be outliers, or suspectedoutliers, or False
                                jitter=0.3, # add some jitter for a better separation between points
                                pointpos=-1.8, # relative position of points wrt box      
                                name= str(b+1)+ ' ' + aa[b],
                                boxmean=True,
                                marker = dict(size=1.5),
                                notched=True,
                                hoveron="boxes",       
                                customdata = [cc[b]],
                                hoverlabel = dict(font=dict(color='white'))       
                                        ))
        else:
            figb.update_layout(annotations=[dict(
                                x=0.5,
                                y=0.5,
                                xref="paper",
                                yref="paper",
                                text="No data available for this selection",
                                showarrow=False)])
        #figb.update_layout(
        #    yaxis = dict(
        #        tickmode = 'array',
        #        tickvals = [ref1,ref2],
        #        ticktext = [str(ref1), str(ref2)]
        #    )
        figb.add_shape(
        # Line Horizontal
            type="line",
            xref = 'paper',
            yref = 'y',
            x0=0,
            y0=ref1,
            x1=1,
            y1=ref1,
            line=dict(
                color="yellow",
                width=2,
                dash="dashdot",
            ))
        figb.add_shape(
        # Line Horizontal
            type="line",
            xref = 'paper',
            yref = 'y',
            x0=0,
            y0=ref2,
            x1=1,
            y1=ref2,
            line=dict(
                color="red",
                width=2,
                dash="dashdot",
            ))
        figb.update_layout(plot_bgcolor="#060606",
          paper_bgcolor="#060606",
          showlegend=False,
          margin=dict(l=0, r=0, t=10, b=30),
          hovermode = 'x unified', 
          font = dict(color='white')
        )
        if axs:
            figb.update_layout(yaxis=dict(range=[0, 2500],
              showgrid=True, 
              zeroline=False, 
              showticklabels=True ))
        else:
            figb.update_layout(yaxis=dict(showgrid=True, 
              zeroline=False, 
              showticklabels=True ))
        figb.update_layout(xaxis=dict(showgrid=False, 
              zeroline=False,
              showticklabels=False  ))
        return figb, selected
    else:
        ef = go.Figure(layout={
        'plot_bgcolor':"#060606",
        'paper_bgcolor':"#060606",
        "xaxis":{"showgrid":False,"zeroline":False,"showticklabels":False},
        "yaxis":{"showgrid":False,"zeroline":False,"showticklabels":False}})
        ef.update_layout(annotations=[dict(
                                x=0.5,
                                y=0.5,
                                xref="paper",
                                yref="paper",
                                text="Hover over spheres to start.",
                                showarrow=False)])
        return ef, 1

@app.callback([Output(component_id='vendor-t2',component_property='children'),
               Output('cur_site','children')],
             [Input(component_id='sphere-boxes',component_property="hoverData")])
def hover_boxplots(box):
    if box != None:
        st = box['points'][0]['x'][2:]
        if box['points'][0]['customdata'] == "Siemens":
            return html.Img(src=siemens_logo,style={"width":"100px"}), html.H6(st,style={"color":"lightgreen"})
        elif box['points'][0]['customdata'] == "Philips":
            return html.Img(src=philips_logo,style={"width":"50px"}), html.H6(st,style={"color":"lightgreen"})
        elif box['points'][0]['customdata'] == "GE":
            return html.Img(src=ge_logo,style={"width":"50px"}), html.H6(st,style={"color":"lightgreen"})
    else:
            return [[],[]]

        
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| TAB 3 CONTENT | BY SITE 
# =========================================================================
#   ______      __         _____
#  /_  __/___ _/ /_       |__  /
#  / / / __ `/ __ \______ /_ < 
# / / / /_/ / /_/ /_____/__/ / 
#/_/  \__,_/_.___/     /____/  


# PHANTOM DISPLAY | TAB3 | phantom-by-site
nist_cockpit3 = dcc.Graph(
        id='phantom-by-site',
        figure=empty_figure,
         config={
        'displayModeBar': False    
        })

# SCATTER-LIKE BOX PLOTS| TAB3 | scatter-by-site
scat_ref = dcc.Graph(
        id='scatter-by-site',
        figure=empty_figure)

# SITE DROPDOWN | TAB3 | dropdown-site-name
site_dropdown = dcc.Dropdown(
    id = "dropdown-site-name",
    placeholder = "Select a site..."
)

# METRIC DROPDOWN | TAB3 | dropdown-site-metric
site_metric = dcc.Dropdown(
    id = "dropdown-site-metric",
        options=[
        {'label': 'Mean', 'value': 'Mean'},
        {'label': 'STD',  'value': 'STD'},
        {'label': 'Median', 'value': 'Median'}, 
        {'label': 'CoV', 'value': 'CoV'},    
    ],
    placeholder = "Select a metric...",
    value = 'Mean'
)  

# SCAN SLIDER | TAB3 | slider-scan
sli_scan=  dcc.Slider(
    min=1,
    max=10,
    step=1,
    id = "slider-scan",
    value =1
)  

# THERMOMETER | TAB3 | thermo-avg-t3
thermo_3 = daq.Thermometer(
        id = "thermo-avg-t3",
        scale={'start': 12, 'interval': 2,
            'labelInterval': 4, 'custom': {
                '20': '(Ref) 20'
            }},
        max = 35,
        value=20,
        width=5,
        height=100,
        showCurrentValue=True,
        style={'color':'#ADAFAE'},
        theme='dark')

# % DIF TOGGLE | TAB3 | toggle-deviation-t3
toggle_deviation_t3 = daq.BooleanSwitch(
    label='% Difference from target',
    labelPosition='bottom',
    id = 'toggle-deviation-t3',
)

# VARIOUS INDICATORS 
vendor_t3 = html.Div(id="vendor-t3",children=[])
scanner_t3 = html.Div(id="scanner-t3",children=[])
data_type = html.Div(id="data-type-t3",children=[])
data_link = html.Div(id="data-link-t3",children=[])

# LED TESLA| TAB3 | led-tesla-t3
led_tesla_t3 = daq.LEDDisplay(
    label="Field Strength (T)",
    value='3',
    color="lightgreen",
    id='led-tesla-t3',
    size=25
)

# LED TR| TAB3 | led-TR
led_TR = daq.LEDDisplay(
    label="TR (ms)",
    value='2550',
    color="lightgreen",
    id='led-TR',
    size=25
)

# LED CONCORDANCE| TAB3 | led-conc
led_conc = daq.LEDDisplay(
    label="Concordance CC",
    color="lightgreen",
    id='led-conc',
    size=25
)

site_metric_label = html.Div(id='site-metric-label',children=[])


# ==========================================================
# T A B 3 - L A Y O U T 
# ========================================================== 
# TODO: ADD TOOLTIPS 
tab3_Layout = dbc.Container(fluid=True,children=[
    dbc.Row([
        # Main Col1
        dbc.Col([html.Br(),
                 html.Center(site_dropdown),
                 html.Br(),
                 html.Center(sli_scan),
                 html.Br(),
                 # Indicators
                 dbc.Row([
                     dbc.Col(site_metric),
                     dbc.Col(toggle_deviation_t3),
                 ],justify="around"),
                 html.Hr(),
                 dbc.Row([
                     dbc.Col(html.Center(led_tesla_t3),align="center"), 
                     dbc.Col(html.Center(thermo_3),align="center"),
                     dbc.Col(html.Center(led_TR),align="center")
                         ],justify="around"),
                 dbc.Row([
                    dbc.Col([html.Center(vendor_t3)]),
                    dbc.Col([html.Center(data_link)]) 
                 ],justify="around",style = {'height':'100px'}),
                 dbc.Row([
                     dbc.Col(html.Center(scanner_t3)),
                     dbc.Col(html.Center(data_type))
                 ],justify="around",style={'height':'50px'}),
                 ],width={"size":4,"offset":0},align="center"),
        # Main Col2
        dbc.Col([html.Center(site_metric_label),html.Br(),html.Center(nist_cockpit3),html.Br(),html.Center(led_conc)],width={"size":4,"offset":0}),
        dbc.Col([html.Br(),html.Center(scat_ref)],width={"size":4,"offset":0}),
    ])
        ])

# ==========================================================
# T A B 3 - C A L L B A C K S
# ========================================================== 
@app.callback([Output('dropdown-site-name','options'),Output('dropdown-site-name','value')],
              [Input('session-id', 'children')])
def populate_dropdown_site(session_id):
    df = get_dataframe(session_id)
    sites = list(df['site name'].value_counts().to_dict().keys())
    options = []
    for site in sites:
        options.append({'label':site,'value':site})
    value = sites[0]
    return options, value

@app.callback([Output('slider-scan','max'),Output('slider-scan','value'),Output('slider-scan','marks')],
              [Input('dropdown-site-name', 'value'),Input('session-id', 'children')])
def populate_dropdown_slider(insite,session_id):
    df = get_dataframe(session_id)
    sites = list(df['site name'].value_counts().to_dict().keys())
    nums = list(df['site name'].value_counts().to_dict().values())
    aa = dict(zip(sites,nums))
    marks= {}
    for ii in range(aa[insite]):
        marks.update({ii+1:str(ii+1)})
    return [aa[insite],1, marks]

image_filename = os.path.join(os.getcwd(), 'assets/img/cloud_link.png')# replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

@app.callback([Output('phantom-by-site','figure'),
               Output('thermo-avg-t3','value'),
               Output('led-tesla-t3','value'),
               Output('led-TR','value'),
               Output('vendor-t3','children'),
               Output('scanner-t3','children'),
               Output('data-type-t3','children'),
               Output('data-link-t3','children'),
               Output('scatter-by-site','figure'),
               Output('led-conc','value'),
               Output('site-metric-label','children')
              ],
              [Input('slider-scan', 'value'),Input('session-id', 'children'),
               Input('dropdown-site-name', 'value'),
               Input('dropdown-site-metric','value'),
               Input('toggle-deviation-t3','on')])
def populate_site_panel(cur_scan,session_id,cur_site,metric,deviation):
    df = get_dataframe(session_id)
    sites = list(df['site name'].value_counts().to_dict().keys())
    if cur_site != None:
        tmp = df[df['site name']==cur_site]
        tmp = tmp.iloc[cur_scan-1]
    else:
        tmp = df[df['site name']==sites[0]]
        tmp = tmp.iloc[0]
    fig = go.Figure()
    temp = tmp['phantom temperature']
    fs = np.round(tmp['MRI field'],2)
    tr = tmp['TR']
    if tmp['MRI vendor'] == 'Siemens':
        vndr = html.Img(src=siemens_logo,style={"width":150})
    elif tmp['MRI vendor'] == "GE":
        vndr = html.Img(src=ge_logo,style={"width":50})
    elif tmp['MRI vendor'] == "Philips":  
        vndr = html.Img(src=philips_logo,style={"width":50})
    if len(tmp['MRI version']) > 15:   
        scanner = html.P(tmp['MRI version'][0:15] +'...',style={"color":'lightgreen'}) 
    else:
        scanner = html.P(tmp['MRI version'],style={"color":'lightgreen'}) 
    dat_type = html.H6('Download ' + tmp['Data type'] + ' Data',style={"color":'lightgreen'})
    dat_link = html.A(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),style={'width':'55px'}),href=tmp['OSF link'],target="_blank")
    NIST_SPHERES = ['T1 - NIST sphere ' + str(ii+1) for ii in range(14)]

    if not np.isnan(tmp['phantom serial number']):
        SN = int(tmp['phantom serial number'])
        if SN<42:
            ver = 'V1'
        else:
            ver = 'V2'
    else:
        SN = 'N/A'
        ver = 'V1'
        
    if metric == 'Mean': 
        t1 = [np.mean(np.array(tmp[sphr])) for sphr in NIST_SPHERES]
        unit = 'ms'
        if deviation:
            t1 = list(np.abs(np.array(t1) - np.array(NIST_REF[ver][metric]))/(np.array(NIST_REF[ver][metric]))*100)
            unit = '%'
        fig = nist_figure(t1,'T1 Plate',6,True,True,SN,unit,'values')
        met = html.H5('Mean',style={'color':'lightgreen'})
    elif metric == 'Median':
        t1 = [np.median(np.array(tmp[sphr])) for sphr in NIST_SPHERES]
        if deviation:
            t1 = list(np.abs(np.array(t1) - np.array(NIST_REF[ver][metric]))/(np.array(NIST_REF[ver][metric]))*100)
            unit = '%'
        fig = nist_figure(t1,'T1 Plate',6,True,True,SN,'ms','values')
        met = html.H5('Median',style={'color':'lightgreen'})
    elif metric == 'STD':
        t1 = [np.std(np.array(tmp[sphr])) for sphr in NIST_SPHERES]
        unit = 'ms'
        met = html.H5('STD',style={'color':'lightgreen'})
        if deviation:
            t1 = list(np.abs(np.array(t1) - np.array(NIST_REF[ver][metric]))/((np.array(t1) + np.array(NIST_REF[ver][metric])))*100)
            unit = '%'
        fig = nist_figure(t1,'T1 Plate',6,True,True,SN,unit,'values')
    elif metric == 'CoV':
        t1 = [np.std(np.array(tmp[sphr]))/np.mean(np.array(tmp[sphr])) for sphr in NIST_SPHERES]
        fig = nist_figure(t1,'T1 Plate',6,True,True,SN,'a.u.','values')
        met = html.H5('CoV',style={'color':'lightgreen'})        
    else:
        t1 = [np.mean(np.array(tmp[sphr])) for sphr in NIST_SPHERES]
        fig = nist_figure(t1,'T1 Plate',6,True,True,SN,'ms','values')  
        met = html.H5('Mean',style={'color':'lightgreen'})       
    boxes = go.Figure()
    t = 0
    for sphr in NIST_SPHERES:
        #cur_val = NIST_REF[ver]['Mean'][t]
        boxes.add_trace(go.Box(y = list(tmp[sphr]),
                               #x = [cur_val]*len(tmp[sphr]),
                               boxpoints='all', # can also be outliers, or suspectedoutliers, or False
                               jitter=0.3, # add some jitter for a better separation between points
                               pointpos=-1.8, # relative position of points wrt box
                               name = 'Sphere ' + str(t+1),
                               boxmean=True,
                               marker = dict(size=1.5),
                               notched=True,
                               hoveron="boxes"
        ))
        t+=1
    boxes.update_layout(height=400,
          plot_bgcolor="#060606",
          paper_bgcolor="#060606",
          showlegend=False,
          margin=dict(l=0, r=0, t=10, b=30),
          hovermode = 'x unified',
          font = dict(color='white'))
    boxes.update_layout(yaxis=dict(range=[-10, 2500],
          showgrid=True, 
          zeroline=False, 
          showticklabels=True ))
    boxes.update_layout(xaxis=dict(autorange='reversed',
          showgrid=False, 
          zeroline=True, 
          showticklabels=False ))
    # Calculate concordance and correlatoin coefficients
    t1_conc = [np.mean(np.array(tmp[sphr])) for sphr in NIST_SPHERES]
    ref_conc = list(NIST_REF[ver]['Mean'])
    concord = calculate_concordance([(t1_conc[ii],ref_conc[ii]) for ii in range(len(t1_conc))])
    return [fig,temp,fs,tr,vndr,scanner,dat_type,dat_link,boxes,concord,met]