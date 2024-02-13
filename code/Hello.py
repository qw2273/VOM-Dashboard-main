# Created by WUQ2 at 7/2/2023
import os
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from htbuilder import HtmlElement, div,  br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from PIL import Image

dir = os.getcwd()
with open(os.path.normpath(os.path.join(dir, "config","credentials.yaml")))as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
name, authentication_status, username = authenticator.login('Logout', 'main')
if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main')
    # set logo
    dir = os.getcwd()
    logo_image = Image.open(os.path.normpath(os.path.join(dir, "img", "wwn_logo.png" ))).resize((500, 150))
    st.image(logo_image)
    st.markdown("### Hello there! 😄 ")
    st.text("")
    st.markdown("#### ⚠️Don't forget to log out after you finish your work.")
    st.sidebar.success("Select a page above")
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning("Please enter username and password")

### add footer
def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))

def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)

def layout(*args):
    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
    </style>
    """

    style_div = styles(
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        text_align="center",
        height="100px",
        opacity=0.6
    )

    style_hr = styles(
    )

    body = p()
    foot = div(style=style_div)(hr(style=style_hr), body)

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)
        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)

def footer():
    myargs = [
        "<b>Made with </b>:  ",
        image('https://streamlit.io/images/brand/streamlit-mark-color.png',
              width=px(16), height=px(16)),
        " with 💗 by ",
        link("http://linkedin.com/in/qqwu", "@Qiqi Wu"),
        br(),
    ]
    layout(*myargs)

if __name__ == "__main__":
    footer()

