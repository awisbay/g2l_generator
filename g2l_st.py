
import streamlit as st
import pandas as pd

from g2l_app import generate_scripts_grouped_by_bsc
from datetime import datetime




st.title("GSM to LTE Script Generator")
st.divider()

st.markdown('Upload a CIQ or Excel file. Please make sure has :red["GSM-LTE-Relation"] Sheet.')
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None, sheet_name="GSM-LTE-Relation")
    df = df.iloc[:, :3]
    df.columns = ['BSC','CELL_GSM', 'EARFCN']   
    df.dropna(subset=['BSC','CELL_GSM', 'EARFCN'], inplace=True)
    df = df[df['CELL_GSM'].str.upper() != 'CELL_GSM']

    cell_options = sorted(df['CELL_GSM'].unique().tolist())
    
    select_all = st.checkbox("Select All Cells")

    if select_all:
        selected_cells = cell_options  # All selected
    else:
        selected_cells = st.multiselect("Select cells to include:", options=cell_options)

    if selected_cells:
        zip_buffer = generate_scripts_grouped_by_bsc(df, selected_cells)
        st.download_button("Download Script", zip_buffer, file_name=f"G2L_scripts_{now_str}.zip", mime="application/zip")