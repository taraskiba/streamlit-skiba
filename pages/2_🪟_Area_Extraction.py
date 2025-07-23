import streamlit as st
from streamlit_folium import folium_static
import geemap as gm
import geemap.foliumap as geemap
import ee
from google.oauth2 import service_account
from ee import oauth
import json

# @st.cache_resource
# def initialize_ee():
#     service_account_info = st.secrets["EARTHENGINE_TOKEN"]
#     credentials = service_account.Credentials.from_service_account_info(service_account_info)
#     ee.Initialize(credentials)
# initialize_ee()  # Initialize the Earth Engine API with token

@st.cache_resource
def ee_initialize(force_use_service_account=False):
    if force_use_service_account or "EARTHENGINE_TOKEN" in st.secrets:
        json_credentials = st.secrets["EARTHENGINE_TOKEN"]
        credentials_dict = json.loads(json_credentials)
        if 'client_email' not in credentials_dict:
            raise ValueError("Service account info is missing 'client_email' field.")
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict, scopes=oauth.SCOPES
        )
        ee.Initialize(credentials)
    else:
        ee.Initialize()
# Initialize GEE
ee_initialize(force_use_service_account=True)

"# streamlit geemap demo"
st.markdown('Source code: <https://github.com/giswqs/geemap-streamlit/blob/main/geemap_app.py>')

with st.echo():
    import streamlit as st
    from streamlit_folium import folium_static
    import geemap.foliumap as geemap
    import ee

    ee_token = st.secrets["EARTHENGINE_TOKEN"]
    gm.ee_initialize(token_name = ee_token, auth_mode = 'cloud')  # Initialize the Earth Engine API with token

    m = geemap.Map()
    dem = ee.Image('USGS/SRTMGL1_003')

    vis_params = {
    'min': 0,
    'max': 4000,
    'palette': ['006633', 'E5FFCC', '662A00', 'D8D8D8', 'F5F5F5']}

    m.addLayer(dem, vis_params, 'SRTM DEM', True, 1)
    m.addLayerControl()

    # call to render Folium map in Streamlit
    folium_static(m)