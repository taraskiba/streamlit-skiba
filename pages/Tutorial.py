import streamlit as st


st.set_page_config(layout="wide")

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

# Customize page title
st.title("User Guide")


st.header("Walkthroughs and FAQs")

st.subheader("Which tools are right for me?")


markdown = """
This app is based on the _skiba_ package and allows users to extract data from Google Earth Engine (GEE) using on a point or area scale.  This package pulls the average pixel value for a specified area for the entire GEE dataset or optional time peroid. Consult the GEE page for the dataset of interest to view the pixel size and time period. \n
Due to some of the _skiba_ package's dependencies not being available in the Streamlit environment, this app is not built with the skiba package. 
Instead, it is recreated in Streamlit to perform the same as queries from Google Earth Engine as done _skiba_ . Many portions of the streamlit version has code pulled directly from the _skiba_ package, but modified to function within Streamlit.
You can compare the _skiba_ package's GitHub page ([_skiba_ on GitHub](https://github.com/taraskiba/skiba.git)) with this app's GitHub page ([_streamlit-skiba_ on GitHub](https://github.com/taraskiba/streamlit-skiba)) for similarities and differences.\n
**Note:** carefully read over instructions for each section to ensure formatting and file types used are correct. \n

*Please be considerate of your energy usage when using this app, as it is hosted on a server and uses Google Earth Engine's resources which contribute significant amounts of carbon. Please run only neccessary queries to minimize your carbon footprint.* \n
"""
st.markdown(markdown)
st.subheader("**_“The greatest threat to our planet is the belief that someone else will save it.”_**")
st.markdown("— Robert Swan ☯ Cheers.")


markdown = """
[tskiba@vols.utk.edu](mailto:tskiba@vols.utk.edu?subject=Skiba%20Package)
for any problems or questions. \n
Google Earth Engine may need to be reauthenticated from time to time.
"""

st.subheader("Email me")
st.markdown(markdown)
