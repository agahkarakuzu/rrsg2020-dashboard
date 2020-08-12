import dash
import dash_bootstrap_components as dbc
import pandas as pd
from flask_caching import Cache
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])
server = app.server

    # TODO: Arrange for deployment
#cache = Cache(server, config={
#    'CACHE_TYPE': 'redis',
    # Note that filesystem cache doesn't work on systems with ephemeral
    # filesystems like Heroku.
#    'CACHE_TYPE': 'filesystem',
#    'CACHE_DIR': 'cache-directory',

    # should be equal to maximum number of users on the app at a single time
    # higher numbers will store more data in the filesystem / redis cache
#    'CACHE_THRESHOLD': 2
# })

cache = Cache()
cache_servers = os.environ.get('MEMCACHIER_SERVERS')
if cache_servers == None:
    # Fall back to simple in memory cache (development)
    cache.init_app(server, config={'CACHE_TYPE': 'simple'})
else:
    cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
    cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
    cache.init_app(server,
        config={'CACHE_TYPE': 'saslmemcached',
                'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                'CACHE_MEMCACHED_USERNAME': cache_user,
                'CACHE_MEMCACHED_PASSWORD': cache_pass,
                'CACHE_OPTIONS': { 'behaviors': {
                    # Faster IO
                    'tcp_nodelay': True,
                    # Keep connection alive
                    'tcp_keepalive': True,
                    # Timeout for set/get requests
                    'connect_timeout': 2000, # ms
                    'send_timeout': 750 * 1000, # us
                    'receive_timeout': 750 * 1000, # us
                    '_poll_timeout': 2000, # ms
                    # Better failover
                    'ketama': True,
                    'remove_failed': 1,
                    'retry_timeout': 2,
                    'dead_timeout': 30}}})

def get_dataframe(session_id):
    @cache.memoize()
    def query_and_serialize_data(session_id):
        
        phan_df = pd.read_pickle('3T_NIST_T1maps_database.pkl')

        return phan_df.to_json()

    return pd.read_json(query_and_serialize_data(session_id))

def get_dataframe_brain(session_id):
    @cache.memoize()
    def query_and_serialize_data(session_id):
        
        brain_df = pd.read_pickle('3T_human_T1maps_database.pkl')

        return brain_df.to_json()

    return pd.read_json(query_and_serialize_data(session_id))

app.config.suppress_callback_exceptions = True