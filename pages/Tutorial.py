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

markdown = """
Slides from September 17, 2025 SNR Seminar and FIA Presentation:
[here](https://github.com/taraskiba/streamlit-skiba/blob/main/skiba_%20a%20forester%E2%80%99s%20package%20to%20retrieve%20Google%20Earth%20Engine%20data.pdf?raw=true)
"""

st.markdown(markdown)

st.header("Walkthroughs and FAQs")

st.subheader("Which tools are right for me?")

markdown = """
![Flowchart](https://github.com/taraskiba/skiba/blob/main/docs/files/flowchart.png?raw=true)
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

st.subheader("Determine your buffer size")
markdown = """
If you are dealing with sensitive data, you may want to use a buffer around your points to avoid exact locations being used. The radius of the buffer size should take into account the radius of you inventory plot and the pixel size of the GEE dataset you are using.
The following figure illustrates some common cases of how points can be buffered, given various plot and pixel sizes.
![Buffered points](https://github.com/taraskiba/skiba/blob/main/docs/files/buffered_diagram.png?raw=true)
Please refer to the upcoming publication and your data's user guide on handling confidential information for more information.
"""
st.markdown(markdown)