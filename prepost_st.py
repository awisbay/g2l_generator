import streamlit as st
import pandas as pd
from prepost_app import posthc_newbsc, prehc_legacybsc


st.title("Generate PreHC and PostHC")
st.divider()

st.markdown('Please Upload MD Template 2G.')
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None, sheet_name="target_cells", skiprows=1)
    df.columns = ['NODENAME','SITENAME','CELL','CELL_DUMMY','BSC_LEGACY','BSC_NEW','RSITE','LOC_CODE','CGI','BSIC','BCCHNO','RXOTG_LEGACY','RXSTG_NEW']
    
    st.markdown(":orange[PreHC Legacy BSC]")
    final_output_pre = prehc_legacybsc(df)
    st.expander("Result PreHC").code(final_output_pre)

    st.divider()
    st.markdown(":green[PostHC New BSC]")
    final_output_post = posthc_newbsc(df)
    st.expander("Result PostHC").code(final_output_post)
    # codetest = st.code(final_output_post)
    # st.text_area("Result", codetest, height=300)