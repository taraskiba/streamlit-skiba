import streamlit as st
import requests
import pandas as pd
import geopandas as gpd
import numpy as np
import io
from pyproj import Transformer
import json
from shapely.geometry import Point
import shapely
import pointpats

# Define functions
@st.cache_data(hash_funcs={shapely.geometry.Point: lambda p: p.wkb})
def create_obfuscated_points(point, radius, no_samp, _crs="EPSG:4326"):
        """
        Create a circle polygon (as a shapely geometry) with the given radius in feet,
        where the provided point is randomly located inside the circle (not at the center) 
        and sample a specifed number of points within the circle.
        """
        # Convert radius from feet to meters
        radius = radius * 0.3048

        # Project to local UTM for accurate distance calculations
        utm_crs = f"EPSG:326{int((point.x + 180) // 6) + 1}"
        transformer_to_utm = Transformer.from_crs(_crs, utm_crs, always_xy=True)
        transformer_to_latlon = Transformer.from_crs(utm_crs, _crs, always_xy=True)
        x, y = transformer_to_utm.transform(point.x, point.y)

        # Randomize the point's location within the circle
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(0, radius)
        # Calculate center of the circle so that the point is inside the circle but not at the center
        center_x = x - distance * np.cos(angle)
        center_y = y - distance * np.sin(angle)
        center = Point(center_x, center_y)

        circle = center.buffer(radius, resolution=32)
        pgon = shapely.geometry.Polygon(circle)

        sampled_points = random_points_in_polygon(pgon, no_samp)
        
        # Transform the circle back to WGS84
        # center_latlon = shapely.ops.transform(
        #     lambda x, y: transformer_to_latlon.transform(x, y), center
        # )
        # return center_latlon
        return sampled_points
       

@st.cache_data(hash_funcs={shapely.geometry.Point: lambda p: p.wkb})
def obfuscate_points(data, radius, no_samp, plot_id_col):
        """
        Obfuscate points within a radius and save as csv.

        Args:
            data (str, pd.DataFrame, gpd.GeoDataFrame): Input data (GeoJSON, DataFrame, or GeoDataFrame).
            radius (float): Radius of the circle in meters.
            plot_id_col (str): Column name for plot IDs.
            output_file (str): Path to save the output GeoJSON file.
        """
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

        centers = []

        for idx, row in gdf.iterrows():
            point = row["geometry"]
            center = create_obfuscated_points(point, radius, no_samp, _crs=gdf.crs)
            for pt in center:
                centers.append({'plot_ID': row[plot_id_col],
                                'lon': pt.x,
                                'lat':pt.y})
            # Create new GeoDataFrame
        df = pd.DataFrame(centers)
        
        return df

def random_points_in_polygon(polygon, num_points):
    minx, miny, maxx, maxy = polygon.bounds
    points = []
    while len(points) < num_points:
        random_point = Point(np.random.uniform(minx, maxx),
                             np.random.uniform(miny, maxy))
        if polygon.contains(random_point):
            points.append(random_point)
    return points

@st.cache_data
def convert_for_download(df):
    return df.to_csv().encode("utf-8")

# Beginning of web app development
st.set_page_config(page_title='Extract GEE Data from Coordinates', layout='wide')

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

st.title("Buffer Sensitive Coordinates by Sampling a Region")
st.header("Optional Prelimiary Step to the Point or Area Extraction Module.")

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
        help="Double check that your CSV file is formatted correctly with LAT and LONG columns.")
    st.markdown("""
                Accepted names for uploaded CSV file: \n
                lat_cols = ['lat', 'latitude', 'y', 'LAT', 'Latitude', 'Y'] \n
                lon_cols = ['lon', 'long', 'longitude', 'x', 'LON', 'Longitude', 'Long', 'X'] \n
                id_cols = ['id', 'ID', 'plot_ID', 'plot_id', 'plotID', 'plotId'] \n
                [Example file](https://raw.githubusercontent.com/taraskiba/streamlit-skiba/refs/heads/main/sample_data/coordinate-point-formatting.csv)
                """)
with col2:
    st.write("Optional: check resolution of Google Earth Engine dataset to determine appropriate buffer area.")
    url = "https://raw.githubusercontent.com/opengeos/geospatial-data-catalogs/master/gee_catalog.json"

    response = requests.get(url)
    data = response.json()

    data_dict = {item["id"]: item["url"] for item in data if "id" in item}
    df = pd.DataFrame(list(data_dict.items()), columns=['id', 'url'])
    geedata = st.selectbox('GEE datasets for reference', df['id'])
    url = data_dict.get(str(geedata))

    st.write('Dataset ID:', url)
    
# Second row
col1, col2, col3 = st.columns(3)
with col1:
    buffer_distance = st.number_input('Step 3: Buffer Distance (in ft)', min_value=0, value=1000, step=1, key='buffer_distance)')

with col2:
    sample_size = st.number_input('Step 4: Number of samples to pull', min_value=0, value=5, step=1, key='sample_size)')

with col3:
    st.button("Reset", type="primary")
    if st.button("Run Query"):
        if uploaded_file is not None:
            file_info = uploaded_file.getvalue()
            points = pd.read_csv(io.BytesIO(file_info))

            lat_cols = ['lat', 'latitude', 'y', 'LAT', 'Latitude', 'Y']
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
                returned_df = obfuscate_points(
                    data=points,
                    radius=buffer_distance,
                    no_samp = sample_size,
                    plot_id_col="plot_ID"
                )
                file_name = f"buffered_coordinates_{buffer_distance}ft.csv"

                csv = convert_for_download(returned_df)

                if csv:
                    st.success("Data extraction complete! You can download the results.")
                    st.download_button(
                        label="Download Results",
                        data=csv,
                        file_name=file_name
                    )
                else:
                    st.error("No data extracted. Please check your inputs and try again.")
                    
        else:
            st.error("Please upload a CSV file with LAT and LONG columns.")    
        
    