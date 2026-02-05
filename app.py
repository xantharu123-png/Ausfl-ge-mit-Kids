import streamlit as st
import streamlit.components.v1 as components

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="🗺️ Jahresguide 2026",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# HIDE STREAMLIT BRANDING
# ============================================================================
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ============================================================================
# LOAD AND RENDER HTML MAP
# ============================================================================
with open('map_template.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

components.html(html_content, height=900, scrolling=False)
