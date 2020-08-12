import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import uuid
from app import app
from apps import home, phantom, brain


#app.layout = html.Div([
#    dcc.Location(id='url', refresh=False),
#    html.Div(id='page-content'),
#    dcc.Link('CHANGE URL', href='/apps/home'),
#    html.Div(session_id, id='session-id', style={'display': 'none'})
#])
server = app.server 

def serve_layout():
    session_id = str(uuid.uuid4())
    return html.Div([
           dcc.Location(id='url', refresh=False),
           html.Div(id='page-content'),
           html.Div(session_id, id='session-id', style={'display': 'none'})
           ])

app.layout = serve_layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
         return home.layout
    elif pathname == '/apps/phantom':
         return phantom.layout
    elif pathname == '/apps/brain':
         return brain.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)