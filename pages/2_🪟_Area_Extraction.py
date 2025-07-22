import streamlit as st
import leafmap.foliumap as leafmap

import ee


# @st.cache_data
# def ee_authenticate(token_name="EARTHENGINE_TOKEN"):
#     ee.initalize(token_name=token_name)

# markdown = """
# A Streamlit map template
# <https://github.com/opengeos/streamlit-map-template>
# """

# st.sidebar.title("About")
# st.sidebar.info(markdown)
# logo = "https://github.com/taraskiba/skiba/blob/a98750c413bd869324c551e7910886b0cd2d2d77/docs/files/logo.png?raw=true"
# st.sidebar.image(logo)


# st.title("Extract GEE Info from GeoJSON files")

# row1, row2, row3, row4 = st.rows([4, 1])


# with col2:

#     basemap = st.selectbox("Select a basemap:", options, index)


# with col1:

#     m = leafmap.Map(
#         locate_control=True, latlon_control=True, draw_export=True, minimap_control=True
#     )
#     m.add_basemap(basemap)
#     m.to_streamlit(height=700)

