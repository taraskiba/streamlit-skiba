import streamlit as st
import requests
import pandas as pd
import numpy as np
import ee
import skiba
import geemap as gm
import geopandas as gpd
import io


ee.Authenticate()
ee.Initialize(project="ee-forestplotvariables")
# os.environ["EARTHENGINE_TOKEN"] == st.secrets["EARTHENGINE_TOKEN"]


st.set_page_config(page_title='Extract GEE Data from Coordinates', layout='wide')

# Customize the sidebar
markdown = """
Web App for the Skiba package
========================
<https://github.com/taraskiba/streamlit-skiba>
"""

# st.sidebar.title("About")
# st.sidebar.info(markdown)
# logo = "https://github.com/taraskiba/skiba/blob/a98750c413bd869324c551e7910886b0cd2d2d77/docs/files/logo.png?raw=true"
# st.sidebar.image(logo)

st.title("Extract GEE Info from Coordinates")
st.header("Extract Data from Google Earth Engine (GEE) using Coordinates in a CSV File.")

# Sidebar filters - # nested sidebar title when duplicated under main one
# st.sidebar.title('Filters') 
# regions = st.sidebar.multiselect('Select Region', df['Region'].unique(), default=df['Region'].unique())
# products = st.sidebar.multiselect('Select Product', df['Product'].unique(), default=df['Product'].unique())

# Filter data
# filtered_df = df[(df['Region'].isin(regions)) & (df['Product'].isin(products))]

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

    return sampled_data

@st.cache_data
def load_gee_as_image(dataset_id, start_date=None, end_date=None, **kwargs):
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
    # Try loading as Image
    try:
        img = ee.Image(dataset_id)
        # If .getInfo() doesn't throw, it's an Image
        img.getInfo()
        return img
    except Exception:
        pass

    # Try loading as ImageCollection
    try:
        col = ee.ImageCollection(dataset_id)
        # If date filters are provided, apply them
        if start_date and end_date:
            col = col.filterDate(start_date, end_date)
        else:
            pass
        # Reduce to a single image (e.g., median composite)
        img = col.median()
        img.getInfo()  # Throws if not valid
        return img
    except Exception:
        pass

    # Try loading as FeatureCollection (convert to raster)
    try:
        fc_temp = ee.FeatureCollection(dataset_id)
        # Convert to raster: burn a value of 1 into a new image
        img = fc_temp.reduceToImage(properties=[], reducer=ee.Reducer.constant(1))
        img.getInfo()
        return img
    except Exception:
        raise ValueError(
            "Dataset ID is not a valid Image, ImageCollection, or FeatureCollection."
        )

# Top row
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Upload a CSV file. The CSV file should contain latitude and longitude columns labeled as LAT and LONG, with a indexing column (no specific column name necessary). Ensure the file is formatted correctly for processing.",
        type=["csv"],
        help="Double check that your CSV file is formatted correctly with LAT and LONG columns.")

with col2:
    url = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"

    response = requests.get(url)
    data = response.json()

    data_dict = {item["id"]: item["url"] for item in data if "id" in item}
    df = pd.DataFrame(list(data_dict.items()), columns=['id', 'url'])
    geedata = st.selectbox('Select a GEE dataset', df['id'])
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

            if not geedata:
                st.error("Please ensure all fields are filled out correctly.")
            else:
                # convert date/time: pd.to_datetime('2024-12-31') 
                returned_dataset = get_coordinate_data(
                    data=points, geedata=geedata, start_date=start_date, end_date=end_date
                )
                
                returned_df = gm.ee_to_df(returned_dataset)
                returned_csv = returned_df.to_csv(index=False)

                
                if returned_csv:
                    st.success("Data extraction complete! You can download the results.")
                    st.download_button(
                        label="Download Results",
                        data=returned_csv,
                        file_name=file_name
                    )
                else:
                    st.error("No data extracted. Please check your inputs and try again.")
                    
        else:
            st.error("Please upload a CSV file with LAT and LONG columns.")    
        
     
