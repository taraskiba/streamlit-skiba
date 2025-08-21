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
![Flowchart](https://github.com/taraskiba/streamlit-skiba/blob/main/sample_data/walkthrough-flowchart.png?raw=true)
"""

st.markdown(markdown)

st.subheader("Common Issues")
markdown = """
**File formatting**: please make sure that your file is formatted in an accepted way. Common issues include 
* unaccepted column names 
* more than just the three neccessary columns
* problems during file conversions (make sure end of csv file does not have extra commas)
* incorrect coordinate formatting (must be in dd.)

**GEE needs reinitialization**: Google Earth Engine needs to be reauthenticated periodically. Please email me to let me know.
"""
st.markdown(markdown)
st.subheader("Point Extraction")

