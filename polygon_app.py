import streamlit as st
import pandas as pd

st.header('Polygon Converter')
st.divider()

# Initialize session state for button click
if 'button_clicked' not in st.session_state:
    st.session_state['button_clicked'] = False

uploaded_file = st.file_uploader("Choose a CIQ file", type="xlsx")
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, "PolygonData")

        # Convert degrees, minutes, and seconds (string) into decimal (float)
        def dms_to_decimal(dms):
            try:
                if isinstance(dms, float):
                    return dms
                # Split the string into degrees, minutes, and seconds
                parts = dms.split('°')
                degrees = float(parts[0])
                minutes_seconds = parts[1].split("'")
                minutes = float(minutes_seconds[0])
                seconds = float(minutes_seconds[1].replace('"', ''))
                
                # Convert to decimal
                decimal = degrees + (minutes / 60) + (seconds / 3600)
                return decimal
            except ValueError as e:
                print(f"Error converting {dms}: {e}")
                return None

        # Text input for filtering
        filter_text = st.text_input("Enter the CELLNAME to filter (comma-separated):", "")

        # Button to generate the transformed DataFrame
        if st.button('Generate'):
            st.session_state['button_clicked'] = True

        if st.session_state['button_clicked']:
            # Split the input text into a list of cell values
            cell_values = [sector.strip() for sector in filter_text.split(',')]

            # Filter the DataFrame based on user input
            filtered_df = df[df['Sector'].isin(cell_values)]

            if filtered_df.empty:
                st.error("CELL NAME NOT IN THIS CIQ")
            else:
                # Column Selection
                selected_columns = filtered_df[['Sector', 'Corner 1', 'Unnamed: 4', 'Corner 2', 'Unnamed: 6', 'Corner 3', 'Unnamed: 8', 'Corner 4', 'Unnamed: 10', 'Corner 5', 'Unnamed: 12', 'Corner 6', 'Unnamed: 14', 'Corner 7', 'Unnamed: 16', 'Corner 8', 'Unnamed: 18', 'Corner 9', 'Unnamed: 20', 'Corner 10', 'Unnamed: 22', 'Corner 11', 'Unnamed: 24', 'Corner 12', 'Unnamed: 26', 'Corner 13', 'Unnamed: 28', 'Corner 14', 'Unnamed: 30', 'Corner 15', 'Unnamed: 32']]

                # Apply the conversion function only to DMS columns
                dms_columns = [col for col in selected_columns.columns if col != 'Sector']
                get_data = selected_columns.copy()
                get_data[dms_columns] = selected_columns[dms_columns].applymap(dms_to_decimal)

                # Fill NaN values with empty strings
                get_data = get_data.fillna("")

                # Define the transformation functions
                def transform_latitude(value):
                    if value != '':
                        return f"0,{round(value * 8388608 / 90)}"
                    return ''

                def transform_longitude(value):
                    if value != '':
                        return f"-{round(value * 16777216 / 360)}"
                    return ''
                
                # Apply the transformations
                for col in dms_columns:
                    if 'Corner' in col:
                        get_data[col] = get_data[col].apply(transform_latitude)
                    elif 'Unnamed' in col:
                        get_data[col] = get_data[col].apply(transform_longitude)

                # Rename columns for display
                get_data.columns = ['Sector'] + [f'Latitude {i//2 + 1}' if i % 2 == 0 else f'Longitude {i//2 + 1}' for i in range(len(get_data.columns) - 1)]

                # Convert the transformed DataFrame to CSV string without quotes and trailing comma
                csv_lines = []
                for index, row in get_data.iterrows():
                    csv_lines.append(','.join([str(item) for item in row if item != '' and item != row['Sector']]))

                csv_string = '\n'.join(csv_lines)

                st.subheader("Data from the Excel file:")
                st.dataframe(get_data, hide_index=True)

                # Display the CSV string in a text area for easy copy-paste
                st.subheader("Transformed DataFrame (CSV format):")
                st.text_area("Copy the CSV data below:", csv_string, height=300)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
else:
    st.info("Please upload an Excel file to view its contents.")