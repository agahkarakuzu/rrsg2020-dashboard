# SITE DROPDOWN | TAB3 | dropdown-site-name
site_dropdown_brain = dcc.Dropdown(
    id = "dropdown-site-name-brain",
    placeholder = "Select a site..."
)

# SCATTER-LIKE BOX PLOTS| TAB3 | scatter-by-site
scat_ref_brain = dcc.Graph(
        id='scatter-by-site-brain',
        figure=empty_figure)

# SCAN SLIDER | TAB3 | slider-scan
sli_scan_brain=  dcc.Slider(
    min=1,
    max=40,
    step=1,
    id = "slider-scan-brain",
    value =1
)  

@app.callback([Output('slider-scan-brain','max'),Output('slider-scan-brain','value'),Output('slider-scan-brain','marks')],
              [Input('dropdown-site-name-brain', 'value'),Input('session-id', 'children')])
def populate_dropdown_slider(insite,session_id):
    df = get_dataframe_brain(session_id)
    sites = list(df['site name'].value_counts().to_dict().keys())
    nums = list(df['site name'].value_counts().to_dict().values())
    aa = dict(zip(sites,nums))
    marks= {}
    for ii in range(aa[insite]):
        marks.update({ii+1:str(ii+1)})
    return [aa[insite],1, marks]

# ==========================================================
# T A B 3 - C A L L B A C K S
# ========================================================== 
@app.callback([Output('dropdown-site-name-brain','options'),Output('dropdown-site-name-brain','value')],
              [Input('session-id', 'children')])
def populate_dropdown_site(session_id):
    df = get_dataframe_brain(session_id)
    sites = list(df['site name'].value_counts().to_dict().keys())
    options = []
    for site in sites:
        options.append({'label':site,'value':site})
    value = sites[0]
    return options, value

# ==========================================================
# T A B 3 - L A Y O U T 
# ========================================================== 
# TODO: ADD TOOLTIPS 
tab3_Layout = dbc.Container(fluid=True,children=[
    dbc.Row([
        # Main Col1
        dbc.Col([html.Br(),
                 html.Center(site_dropdown_brain),
                 html.Br(),
                 html.Center(sli_scan_brain),
                 #html.Br(),
                 # Indicators
                 #dbc.Row([
                 #    dbc.Col(site_metric),
                 #    dbc.Col(toggle_deviation_t3),
                 #],justify="around"),
                 html.Hr(),
                 #dbc.Row([
                     #dbc.Col(html.Center(led_tesla_t3),align="center"), 
                     #dbc.Col(html.Center(thermo_3),align="center"),
                     #dbc.Col(html.Center(led_TR),align="center")
                #         ],justify="around"),
                 #dbc.Row([
                 #   dbc.Col([html.Center(vendor_t3)]),
                 #   dbc.Col([html.Center(data_link)]) 
                 #],justify="around",style = {'height':'100px'}),
                 #dbc.Row([
                 #    dbc.Col(html.Center(scanner_t3)),
                 #    dbc.Col(html.Center(data_type))
                 #],justify="around",style={'height':'50px'}),
                 ],width={"size":6,"offset":0},align="center"),
        dbc.Col([html.Br(),html.Center(scat_ref_brain)],width={"size":4,"offset":0}),
    ])
        ])