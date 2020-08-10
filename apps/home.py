import numpy as np
import matplotlib.pyplot as plt
import math
import plotly.graph_objects as go
import plotly.colors as co
from jupyter_dash import JupyterDash
import pandas as pd 
import plotly.express as px
import base64
from app import app
import matplotlib.cm as m_cmap
import matplotlib.colors as m_colors
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import dash_daq as daq
import dash_bootstrap_components as dbc

# TODO: Use cached data here later on
# Read brain database in pickle format as is does not require format conversion
brain_df = pd.read_pickle('https://github.com/rrsg2020/analysis/blob/master/databases/3T_human_T1maps_database.pkl?raw=true')
phan_df = pd.read_pickle('https://github.com/rrsg2020/analysis/blob/master/databases/3T_NIST_T1maps_database.pkl?raw=true')

# Merge datasets for Sankey chart
frames = [brain_df, phan_df]
rrsg_df = pd.concat(frames,keys=['Brain', 'Phantom'])

def get_vendor_per_site(sources,targets,values,site_dict,df): 
    # Create target IDs for the vendors 
    vendors = list(df['MRI vendor'].value_counts().to_dict().keys())
    site_ids = [site_dict[x]['id'] for x in site_dict]
    vendor_ids = list(range(np.max(site_ids)+1,np.max(site_ids)+1+len(vendors)))
    vendor_dict = dict(zip(vendors,vendor_ids))
    for site in site_dict:
        cur_key = list(df[df['site name']==site]['MRI vendor'].value_counts().to_dict().keys())
        cur_val = list(df[df['site name']==site]['MRI vendor'].value_counts().to_dict().values())
        [targets.append(vendor_dict[key]) for key in cur_key]
        [sources.append(site_dict[site]['id']) for key in cur_key]
        [values.append(val) for val in cur_val]

    return sources, targets, values, vendors

def get_site_dict(df): 
    # Site IDs will start from 2 as 0-1 are for Brain and Phantom
    sites = list(df['site name'].value_counts().to_dict().keys())
    sub_tot = list(df['site name'].value_counts().to_dict().values())
    ids = list(range(2,len(sites)+2))
    site_dict = {}
    for ii in range(len(sites)):
        site_dict.update({sites[ii]:{'id':ids[ii],
                                    'total':sub_tot[ii],
                                    'brain':np.sum(rrsg_df.loc['Brain']['site name'] == sites[ii]),
                                    'phantom':np.sum(rrsg_df.loc['Phantom']['site name'] == sites[ii])
                                    }})
    return site_dict

def get_site_sankey(sources,targets,values,submit_type,site_dict):
    if submit_type == 'brain':
        idx = 0
    elif submit_type == 'phantom':
        idx = 1    
    for site in site_dict:
        if not site_dict[site][submit_type] == 0:
            sources.append(idx)
            targets.append(site_dict[site]['id'])
            values.append(site_dict[site][submit_type])

    return sources,targets,values

def hex2rgba(instr,opacity):
    h = instr.lstrip('#')
    tmp = 'rgba' + str(tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))
    tmp = tmp[0:-1] + ', ' + str(opacity) + ')'
    return tmp

def get_link_lookup(list_in,map_name,opacity):
    cmap = m_cmap.get_cmap(map_name)
    norm = m_colors.Normalize(vmin=np.min(list_in),vmax=np.max(list_in))
    colors = []
    for ii in list_in:
        tmp =  list((np.array(cmap(norm(ii)))*255).astype('uint8'))
        cur_color = 'rgba(' + str(tmp[0]) + ',' + str(tmp[1]) + ',' + str(tmp[2]) + ','+ str(opacity) + ')'
        colors.append(cur_color)
    return colors  

sources = []
labels = []
values = []
targets = []

# Get dictionary per site that contains: 
# site ID & N total, brain and phantom submissions 
site_dict = get_site_dict(rrsg_df)

# Set first two labels 
labels.append('Brain')
labels.append('Phantom')

# Get sankey values for sites
sources,targets,values = get_site_sankey(sources,targets,values,'brain',site_dict)
sources,targets,values = get_site_sankey(sources,targets,values,'phantom',site_dict)

# Concat node labels for sites
site_names = [x for x in site_dict]
labels += site_names

sources, targets, values, vendor_labels = get_vendor_per_site(sources,targets,values,site_dict,rrsg_df)

# Concat node labels for vendors
labels += vendor_labels

# GENERATE SANKEY LINK COLORS ==============================================

matches = (x for x in sources if x == 0)
zrs = len(list(matches))

matches = (x for x in sources if x == 1)
ons = len(list(matches))

# Get all site IDS 
site_ids = [site_dict[x]['id'] for x in site_dict]

# These are for the links from the first input
# Brain: Yellow 
# Phantom: Green  
source_link_clrs = ['rgba(254, 192, 47,0.6)']*zrs + ['rgba(38, 169, 108,0.6)']*ons

# In the sources list, what follows after source_link ids are site IDs, as 
# vendors are not added as a source to a target. 

site_link_clrs = get_link_lookup(sources[zrs+ons:],'Spectral_r',0.5)

link_clrs = source_link_clrs + site_link_clrs

# GENERATE SANKEY NODE COLORS ==============================================
# The rest of color list for the links (2-->n_sites) are going to be 
# created by matplotlib colorscales using get_link_lookup 

# Nodes should not be transparent
site_node_clrs =  list(get_link_lookup(site_ids,'Spectral_r',1))
source_node_clrs = ['rgba(254, 192, 47,1)','rgba(38, 169, 108,1)']
vendor_clrs = ['#3b78ad','#c4a78b','#159494'] 
node_clrs = source_node_clrs + site_node_clrs + vendor_clrs 

# GENERATE SANKEY FIGURE ==============================================
fig = go.Figure(data=[go.Sankey(
    textfont = dict(size=14,family="Open Sans",color="white"),
    node = dict(
      pad = 30,
      thickness = 30,
      label = labels,
      x= [0.001,0.001,0.5] + [0.3]*23 + [1,1,0.9],
      y = [0.75,0.001,0.0001] + list(np.linspace(0.1,1.1,23)) + [1,0.2,0.6],  
      color = node_clrs
    ),
    link = dict(
      source = sources,
      target = targets,
      value = values,
      color = link_clrs
  ))])

fig.update_layout(plot_bgcolor="#060606",paper_bgcolor="#060606",margin=dict(l=10, r=10, t=30, b=60))
fig.update_layout(height=400)

image_filename = os.path.join(os.getcwd(), 'assets/img/brain.gif')
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
card1 = html.Div([
    html.A(
    html.Img(src='data:image/gif;base64,{}'.format(encoded_image.decode()),width='300px'),
    href="google.com"    
    )
])


image_filename = os.path.join(os.getcwd(), 'assets/img/phantom.gif')
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
card2 = html.Div([
    html.A(
    html.Img(src='data:image/gif;base64,{}'.format(encoded_image.decode()),width='300px'),
    href="/apps/phantom",
    target = '_blank'
    )
])

image_filename = os.path.join(os.getcwd(), 'assets/img/title.png')
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
title_img = html.Div([

    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),width='300px') 

])

toast_phantom = dbc.Toast(
        "Explanation about human acq goes here.",
        id="positioned-toast-phantom",
        header="ISMRM/NIST Phantom",
        is_open=False,
        dismissable=True,
        duration='5000',
        icon="success",
        # top: 66 positions the toast below the navbar
        style={"position": "fixed", "top": 66, "left": 100, "width": 1000,'color':'#060606'},
        header_style={"color":'white','background-color':'#26a96c'}
)

toast_human = dbc.Toast(
        "Explanation about human acquisition goes here.",
        id="positioned-toast-human",
        header="Human Data",
        is_open=False,
        dismissable=True,
        duration='5000',
        icon="warning",
        # top: 66 positions the toast below the navbar
        style={"position": "fixed", "top": 66, "right": 100, "width": 1000,'color':'#060606'},
        header_style={"color":'white','background-color':'#fec02f'}
    )

row = html.Div(
    [           
        dbc.Row(
            [   dbc.Col(
                dbc.Button(
               "About Phantom Data", id="phan_button", color='light'
                ),width=1,align='center'),
                dbc.Col(
                    card2,
                    width=3

                ),
                dbc.Col(
                    title_img,
                    width=3
                ),
                dbc.Col(
                    card1,
                    width=3

                ),
                dbc.Col(
                dbc.Button(
               "About Human Data", id="human_button", color='light'
                ),width=1,align='center')
            ],
             justify = 'center',
             style={

              'margin-top' : '1vh'}   
            
        ),
        html.Center(
        dbc.Row([   
         dbc.Col(dcc.Graph(figure=fig,config={
        'displayModeBar': False
        },style={'color':'white'}),width={"size": 10,"offset":1})   
        ])),
        toast_phantom,
        toast_human
    ]

)

layout=html.Div(children=[
    dbc.Container(fluid=True,children=[
      row  
    ])    
])

@app.callback(
    Output("positioned-toast-phantom", "is_open"),
    [Input("phan_button", "n_clicks")],
)
def open_toast(n):
    if n:
        return True
    return False

@app.callback(
    Output("positioned-toast-human", "is_open"),
    [Input("human_button", "n_clicks")],
)
def open_toast(n):
    if n:
        return True
    return False