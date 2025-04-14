import streamlit as st
import pandas as pd
from datetime import datetime
from zipfile import ZipFile

# Function to determine RATPRIO
def get_ratprio(earfcn):
    if earfcn in [5060, 5070, 5145, 5815, 2435, 2436, 2426]:
        return 6
    elif earfcn in [2050, 2025, 2000, 2350, 675, 700, 1025, 1075, 1050]:
        return 5
    elif earfcn in [3050, 3150, 2950, 2900]:
        return 4
    else:
        return 4

st.title("GSM to LTE Script Generator")
st.divider()
st.subheader('Upload a CIQ or excel file. Please make sure has sheet name "GSM-LTE-Relation"')
uploaded_file = st.file_uploader("Choose a file", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, header=None, sheet_name="GSM-LTE-Relation")
        df.columns = ['BSC','CELL_GSM', 'EARFCN']
        df.dropna(subset=['BSC','CELL_GSM', 'EARFCN'], inplace=True)
        df['CELL_GSM'] = df['CELL_GSM'].astype(str).str.strip()
        df = df[df['CELL_GSM'].str.upper() != 'CELL_GSM']
        
        bsc_groups = df.groupby('BSC')
        generated_files = {}
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get unique CELLs
        unique_cells = sorted(df['CELL_GSM'].unique().tolist())
        
        st.divider()
        st.text("Please select desire CELL to generate")
        # Select All toggle
        kol1, kol2 = st.columns([3,1])
        with kol2:
            select_all = st.checkbox("Select All")

        selected_cells = []

        for i, cell in enumerate(unique_cells):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<div style='margin-top: 6px'>{cell}</div>", unsafe_allow_html=True)
            with col2:
                checked = st.checkbox("", key=f"chk_{cell}", value=select_all)
                if checked:
                    selected_cells.append(cell)

        if selected_cells:
            output = []

            for cell in selected_cells:
                group = df[df['CELL_GSM'] == cell]
                earfcns = group['EARFCN'].tolist()
                fddarfcn_combined = '&'.join(map(str, earfcns))

                script = f"""RLUMP:CELL={cell};

RLSRP:CELL={cell};
RLSRC:CELL={cell},FDDARFCN=1037,RATPRIO=3,HPRIOTHR=4;
RLSRP:CELL={cell};

RLEFP:CELL={cell};
RLEFC:CELL={cell},ADD,EARFCN={fddarfcn_combined},LISTTYPE=IDLE;"""

                for earfcn in earfcns:
                    ratprio = get_ratprio(earfcn)
                    script += f"\nRLSRC:CELL={cell},EARFCN={earfcn},RATPRIO={ratprio},HPRIOTHR=7;"

                script += f"""\nRLSRP:CELL={cell};

RLSRC:CELL={cell},RATPRIO=1;
RLSRI:CELL={cell};
RLSRP:CELL={cell};"""

                output.append(script)

            final_output = '\n\n'.join(output)

            st.text_area("Result", final_output, height=500)

            st.download_button(
                label="Download Script",
                data=final_output,
                file_name="G2L_Script.txt",
                mime="text/plain"
            )
        else:
            st.info("✅ Please select at least one CELL to generate the script.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
