import streamlit as st
import pandas as pd
from prepost_app import posthc_newbsc, prehc_legacybsc


st.title("Generate PreHC and PostHC")
st.divider()

st.markdown('Please Upload MD Template 2G.')
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, header=None, sheet_name="target_cells", skiprows=1)
        
        # Define the expected column names
        expected_columns = ['NODENAME','SITENAME','CELL','CELL_DUMMY','BSC_LEGACY','BSC_NEW','RSITE','LOC_CODE','CGI','BSIC','BCCHNO','RXOTG_LEGACY','RXSTG_NEW']
        
        # Check if we have enough columns
        if len(df.columns) < len(expected_columns):
            st.error(f"Error: Excel file has {len(df.columns)} columns, but we need at least {len(expected_columns)} columns.")
            st.error("Please check that your Excel file has the correct format.")
        else:
            # Only assign names to the first 13 columns we need
            for i, col_name in enumerate(expected_columns):
                df.rename(columns={df.columns[i]: col_name}, inplace=True)
            
            # Display file info
            st.info(f"File loaded successfully: {len(df.columns)} columns, {len(df)} rows")
            st.info(f"Using columns: {', '.join(expected_columns)}")
            
            # Show sample data
            with st.expander("Preview data (first 5 rows)"):
                st.dataframe(df[expected_columns].head())
        
            st.markdown(":orange[PreHC Legacy BSC]")
            final_output_pre = prehc_legacybsc(df)
            st.expander("Result PreHC").code(final_output_pre)

            st.divider()
            st.markdown(":green[PostHC New BSC]")
            final_output_post = posthc_newbsc(df)
            st.expander("Result PostHC").code(final_output_post)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
        st.error("Please check that your Excel file:")
        st.error("- Has a 'target_cells' sheet")
        st.error("- Contains the expected columns")
        st.error("- Is in the correct Excel format (.xlsx)")
else:
    st.warning("Please upload the Excel file.")