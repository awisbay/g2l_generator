import streamlit as st
import pandas as pd
from zipfile import ZipFile
from io import BytesIO
from datetime import datetime

def get_ratprio(earfcn):
    if earfcn in [5060, 5070, 5145, 5815, 2435, 2436, 2426]:
        return 6
    elif earfcn in [2050, 2025, 2000, 2350, 675, 700, 1025, 1075, 1050]:
        return 5
    elif earfcn in [3050, 3150, 2950, 2900]:
        return 4
    else:
        return 4

#function to generate script and zip file
def generate_scripts_grouped_by_bsc(df, selected_cells):
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    df = df[df['CELL_GSM'].isin(selected_cells)]
    bsc_groups = df.groupby('BSC')
    generated_files = {}

    for bsc, group in bsc_groups:
        cells = group['CELL_GSM'].unique().tolist()
        script_lines = []

        for cell in cells:
            earfcns = group[group['CELL_GSM'] == cell]['EARFCN'].tolist()
            fddarfcn_combined = '&'.join(map(str, earfcns))
            #write parameter to script
            section = f"""RLUMP:CELL={cell};

RLSRP:CELL={cell};
RLSRC:CELL={cell},FDDARFCN=1037,RATPRIO=3,HPRIOTHR=4;
RLSRP:CELL={cell};

RLEFP:CELL={cell};
RLEFC:CELL={cell},ADD,EARFCN={fddarfcn_combined},LISTTYPE=IDLE;"""

            for earfcn in earfcns:
                ratprio = get_ratprio(earfcn)
                section += f"\nRLSRC:CELL={cell},EARFCN={earfcn},RATPRIO={ratprio},HPRIOTHR=7;"

            section += f"""\nRLSRP:CELL={cell};

RLSRC:CELL={cell},RATPRIO=1;
RLSRI:CELL={cell};
RLSRP:CELL={cell};"""
            script_lines.append(section)

        joined_cells = '&'.join(cells)
        closing = f"\nIOEXP;\nRLEFP:CELL={joined_cells};\nRLSRP:CELL={joined_cells};\nCACLP;"
        full_script = '\n\n'.join(script_lines) + closing
        filename = f"{bsc}_G2L_{now_str}.txt"
        generated_files[filename] = full_script

    #zip file
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zipf:
        for filename, content in generated_files.items():
            zipf.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer

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