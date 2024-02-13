# Created by WUQ2 at 7/2/2023

import streamlit as st
from PIL import Image
import os
dir = r"C:\Users\wuq2\Documents\wwn\vom"

# # set logo
st.set_page_config(
    page_title="WWN",
    # layout="wide",
    page_icon="👋",
)
logo_image = Image.open(os.path.normpath(os.path.join(dir, "img", "wwn_logo.jpg")))
st.image(logo_image)

st.write("# Welcome to WWN! 👋")

st.sidebar.success("Select a page above.")

# st.markdown(
#     """
#     Streamlit is an open-source app framework built specifically for
#     Machine Learning and Data Science projects.
#     **👈 Select a demo from the sidebar** to see some examples
#     of what Streamlit can do!
#     ### Want to learn more?
#     - Check out [streamlit.io](https://streamlit.io)
#     - Jump into our [documentation](https://docs.streamlit.io)
#     - Ask a question in our [community
#         forums](https://discuss.streamlit.io)
#     ### See more complex demos
#     - Use a neural net to [analyze the Udacity Self-driving Car Image
#         Dataset](https://github.com/streamlit/demo-self-driving)
#     - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
# """
# )