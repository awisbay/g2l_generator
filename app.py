from get_data import generate_scripts_grouped_by_bsc
import streamlit as st
import pandas as pd



st.title("GSM to LTE Script Generator")
st.divider()

st.markdown('Upload a CIQ or Excel file. Please make sure has :red["GSM-LTE-Relation"] Sheet.')
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None, sheet_name="GSM-LTE-Relation")
    df.columns = ['BSC','CELL_GSM', 'EARFCN']
    df.dropna(subset=['BSC','CELL_GSM', 'EARFCN'], inplace=True)
    df = df[df['CELL_GSM'].str.upper() != 'CELL_GSM']

    cell_options = sorted(df['CELL_GSM'].unique().tolist())
    selected_cells = []

    st.write("Select cells to include:")
    kol1, kol2 = st.columns([3,1])
    with kol2:
        select_all = st.checkbox("Select All")


    for i, cell in enumerate(cell_options):
        cols = st.columns([3, 1])
        with cols[0]:
            st.write(cell)
        with cols[1]:
            checked = st.checkbox("", key=f"chk_{cell}", value=select_all)
            if checked:
                selected_cells.append(cell)

    if selected_cells:
        zip_buffer = generate_scripts_grouped_by_bsc(df, selected_cells)
        st.download_button("Download Script", zip_buffer, file_name="G2L_scripts.zip", mime="application/zip")