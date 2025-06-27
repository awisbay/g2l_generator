import streamlit as st


g2l_generator = st.Page("g2l_st.py", title="GSM To LTE Script Generator", icon="⚙️")
prepost_hc = st.Page("prepost_st.py", title="Pre/Post HC Log Generator", icon="🩺")
polygon_app = st.Page("polygon_app.py", title="Polygon Converter", icon="✴️")
modump_downloader = st.Page("getlistfile.py", title="Sunset Modump", icon="🔽")
allip_downloader = st.Page("allip.py", title="Allip BSC", icon="🔽")
migration = st.Page("migration.py", title="Migration Modump", icon="🔽")
rbsdump = st.Page("rbsdump.py", title="RBS Sunset Modump", icon="🔽")

pg = st.navigation(
    {
        "2G Migration" : [g2l_generator, prepost_hc],
        "3G Migration" : [polygon_app],
        "Downloader" : [modump_downloader, allip_downloader, migration, rbsdump]
    }
)
st.set_page_config(page_title="IRS Migration Tools", page_icon="🛡", layout="wide")
pg.run()