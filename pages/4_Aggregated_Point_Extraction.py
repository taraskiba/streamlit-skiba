import streamlit as st
import requests
import pandas as pd
import numpy as np
import ee
import geemap as gm
import geopandas as gpd
import io
from google.oauth2 import service_account
from ee import oauth
import json

# When running locally, use the following lines to authenticate and initialize Earth Engine
#ee.Authenticate()  # Authenticate with Google Earth Engine when using locally
#ee.Initialize(project="ee-forestplotvariables")  # Initialize the Earth Engine API

# When deploying onto remote server, run the following
# @st.cache_resource
# def initialize_ee():
#     service_account_info = st.secrets["EARTHENGINE_TOKEN"]
#     credentials = service_account.Credentials.from_service_account_info(service_account_info)
#     ee.Initialize(credentials)
# initialize_ee()  # Initialize the Earth Engine API with token

@st.cache_resource
def ee_initialize(force_use_service_account=False):
    if force_use_service_account or "EARTHENGINE_TOKEN" in st.secrets:
        ### Make sure to replace \n with \\n in updated secrets
        # to ensure valid JSON format
        json_credentials = st.secrets["EARTHENGINE_TOKEN"]
        json_credentials = json_credentials.replace("'", "\"")  # Ensure valid JSON format
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


@st.cache_data 
def get_coordinate_data(data, geedata, start_date, end_date, **kwargs):
    """
    Pull data from provided coordinates from GEE.

    Args:
        data (str): The data to get the coordinate data from.

    Returns:
        data (str): CSV file contained GEE data.
    """
    
    # Load data with safety checks
    if isinstance(data, str):
        coordinates = pd.read_csv(data)
        gdf = gpd.GeoDataFrame(
            coordinates,
            geometry=gpd.points_from_xy(coordinates.LON, coordinates.LAT),
            crs="EPSG:4326",  # Directly set CRS during creation
        )
    elif isinstance(data, pd.DataFrame):
        coordinates = data
        gdf = gpd.GeoDataFrame(
            coordinates,
            geometry=gpd.points_from_xy(coordinates.LON, coordinates.LAT),
            crs="EPSG:4326",  # Directly set CRS during creation
        )
    else:
        gdf = data.to_crs(epsg=4326)  # Ensure WGS84
        

    geojson = gdf.__geo_interface__
    fc = gm.geojson_to_ee(geojson)
    
    dataset_id = f"{geedata}"

    # Load the GEE dataset as an image
    geeimage = load_gee_as_image(dataset_id=dataset_id, start_date=start_date, end_date=end_date)

    # Retrieve data from the image using sampleRegions
    sampled_data = gm.extract_values_to_points(fc, geeimage, scale = None)
    sampled_df = gm.ee_to_df(sampled_data)
    filtered_df = sampled_df.drop(['LAT', 'LON', 'Unnamed: 0'], axis = 1)
    st.write("Pre-aggregation data preview:")
    st.write(filtered_df.head())
    aggregated_df = filtered_df.groupby('plot_ID').mean()
    
    id_col = sampled_data.pop('plot_ID')
    sampled_data.insert(0, 'plot_ID', id_col)  # Insert at the beginning
    sampled_data = sampled_data.drop(columns = ['Unnamed'])
    
    return aggregated_df

@st.cache_data
def load_gee_as_image(dataset_id, start_date, end_date, **kwargs):
    """
    Loads any GEE dataset (Image, ImageCollection, FeatureCollection) as an ee.Image.
    Optionally filters by start and end date if applicable.

    Parameters:
        dataset_id (str): The Earth Engine dataset ID.
        start_date (str): Optional start date in 'YYYY-MM-DD' format.
        end_date (str): Optional end date in 'YYYY-MM-DD' format.

    Returns:
        ee.Image: The resulting image.
    """
    url = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"
    response = requests.get(url)
    response.raise_for_status()  # Raises an exception for HTTP errors
    geojson_data = response.json()

    data_type =[item["type"] for item in geojson_data if item["id"]==dataset_id]
    data_str = ' '.join(data_type)
    start_date = str(start_date)
    end_date = str(end_date)

    # Try loading as Image
    if data_str == "image":
        img = ee.Image(dataset_id)
        # If .getInfo() doesn't throw, it's an Image
        img.getInfo()
        return img
    elif data_str == "image_collection":
        col = ee.ImageCollection(dataset_id)
        # If date filters are provided, apply them
        if start_date is None and end_date is None:
            col = col.filterDate(start_date, end_date)
        else:
            pass
        # Reduce to a single image (e.g., median composite)
        img = col.median()
        return img
    # Try loading as FeatureCollection (convert to raster)
    else:
        fc_temp = ee.FeatureCollection(dataset_id)
        if start_date is None and end_date is None:
                fc_temp = fc_temp.filterDate(start_date, end_date)
        # Convert to raster: burn a value of 1 into a new image
        img = fc_temp.reduceToImage(properties=[], reducer=ee.Reducer.median())
        img.getInfo()
        return img
        # or print(f"Dataset must be either an Image or Image Collection")
        # except Exception:
        #     raise ValueError(
        #         "Dataset ID is not a valid Image, ImageCollection, or FeatureCollection."
        #     )

@st.cache_data
def convert_df(df):
    return df.to_csv().encode("utf-8")

# Beginning of web app development
st.set_page_config(page_title='Extract GEE data and average over matching plot ID', layout='wide')

# Customize the sidebar
markdown = """
Web App for the Skiba package
========================
<https://github.com/taraskiba/streamlit-skiba>
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://github.com/taraskiba/skiba/blob/a98750c413bd869324c551e7910886b0cd2d2d77/docs/files/logo.png?raw=true"
st.sidebar.image(logo)

st.title("Extract GEE data and average over matching plot ID")
st.header("Secondary Step to *Buffer and Sample*")

# Sidebar filters - # nested sidebar title when duplicated under main one
# st.sidebar.title('Filters') 
# regions = st.sidebar.multiselect('Select Region', df['Region'].unique(), default=df['Region'].unique())
# products = st.sidebar.multiselect('Select Product', df['Product'].unique(), default=df['Product'].unique())

# Filter data
# filtered_df = df[(df['Region'].isin(regions)) & (df['Product'].isin(products))]

# Top row
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Step 1: Upload a CSV file.",
        type=["csv"],
        help="Double check that your CSV file is formatted correctly with accepted latitude and longitude columns.")
    markdown = """
                Accepted names for uploaded CSV file: \n
                | **CSV Columns** | **Accepted Names**                                |
                |-----------------|---------------------------------------------------|
                | latitude        | lat, latitude, y, LAT, Latitude, Lat, Y                |
                | longitude       | log, long, longitude, x, LON, Longitude, Long, X  |
                | plot ID         | id, ID, plot_ID, plot_id, plotID, plotId          |
                
                [Example file](https://raw.githubusercontent.com/taraskiba/streamlit-skiba/refs/heads/main/sample_data/coordinate-point-formatting.csv)
                """
    st.markdown(markdown)
with col2:
    url = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"

    response = requests.get(url)
    data = response.json()

    data_dict = {item["id"]: item["url"] for item in data if "id" in item}
    df = pd.DataFrame(list(data_dict.items()), columns=['id', 'url'])
    geedata = st.selectbox('Step 2: Select a GEE dataset', df['id'])
    url = data_dict.get(str(geedata))

    st.write('Dataset ID:', url)
    geedata = str(geedata)
    geedata_stripped = geedata.strip()
    file_name = geedata_stripped.replace("/", "_")
    st.write('Your file will be downloaded under the following name:', file_name,'.csv')

# Second row
col1, col2, col3 = st.columns(3)
with col1:
    start_date = st.date_input('(Optional) Start Date', value=None)

with col2:
    end_date = st.date_input('(Optional) End Date', value=None)

with col3:
    st.button("Reset", type="primary")
    if st.button("Run Query"):
        if uploaded_file is not None:
            file_info = uploaded_file.getvalue()
            points = pd.read_csv(io.BytesIO(file_info))

            lat_cols = ['lat', 'latitude', 'y', 'LAT', 'Latitude', 'Lat', 'Y']
            lon_cols = ['lon', 'long', 'longitude', 'x', 'LON', 'Longitude', 'Long', 'X']
            id_cols = ['id', 'ID', 'plot_ID', 'plot_id', 'plotID', 'plotId']

            def find_column(possible_names, columns):
                for name in possible_names:
                    if name in columns:
                        return name
                # fallback: check case-insensitive match
                lower_columns = {c.lower(): c for c in columns}
                for name in possible_names:
                    if name.lower() in lower_columns:
                        return lower_columns[name.lower()]
                raise ValueError(f"No matching column found for {possible_names}")

            lat_col = find_column(lat_cols, points.columns)
            lon_col = find_column(lon_cols, points.columns)
            id_col = find_column(id_cols, points.columns)

            points = points.rename(columns={lat_col: 'LAT', lon_col: 'LON', id_col: 'plot_ID'})

            if not geedata:
                st.error("Please ensure all fields are filled out correctly.")
            else:
                # convert date/time: pd.to_datetime('2024-12-31') 
                returned_dataset = get_coordinate_data(
                    data=points, geedata=geedata, start_date=start_date, end_date=end_date
                )
                
                returned_csv = convert_df(returned_dataset)

                if returned_csv:
                    st.success("Data extraction complete! You can download the results.")
                    st.download_button(
                        label="Download Results",
                        data=returned_csv,
                        mime="text/csv",
                        file_name=f"{file_name}.csv"
                    )
                else:
                    st.error("No data extracted. Please check your inputs and try again.")
                    
        else:
            st.error("Please upload a CSV file with LAT and LONG columns.")    
        
     
