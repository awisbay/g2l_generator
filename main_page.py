import streamlit as st


g2l_generator = st.Page("g2l_st.py", title="GSM To LTE Script Generator", icon=":material/cable:")
prepost_hc = st.Page("prepost_st.py", title="Pre/Post HC Log Generator", icon=":material/api:")
polygon_app = st.Page("polygon_app.py", title="Polygon Converter", icon=":material/terrain:")

pg = st.navigation(
    {
        "2G Migration" : [g2l_generator, prepost_hc],
        "3G Migration" : [polygon_app]
    }
)
st.set_page_config(page_title="IRS Migration Tools", page_icon="🛡")
pg.run()