import streamlit as st
import leafmap.foliumap as leafmap


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


st.title("Interactive Map")

with st.expander("See source code"):
    with st.echo():
        m = skiba.Map()
m.to_streamlit(height=700)
