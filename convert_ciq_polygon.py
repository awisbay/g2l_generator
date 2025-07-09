import pandas as pd
import streamlit as st
import re

def convert_degree_to_decimal(degree_str):
    """
    Convert degree format (e.g., "45°29'53.0"N") to decimal format
    """
    if pd.isna(degree_str) or degree_str == '':
        return None
    
    # Remove any whitespace
    degree_str = str(degree_str).strip()
    
    # Pattern to match degrees, minutes, seconds format
    # Example: 45°29'53.0"N or -73°33'1.0"W
    pattern = r"(-?\d+)°(\d+)'([\d.]+)\"?([NSEW])?"
    match = re.match(pattern, degree_str)
    
    if match:
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        direction = match.group(4) if match.group(4) else ''
        
        # Convert to decimal
        decimal = abs(degrees) + minutes/60 + seconds/3600
        
        # Apply sign based on direction or original sign
        if degrees < 0 or direction in ['S', 'W']:
            decimal = -decimal
            
        return decimal
    else:
        # Try to parse as already decimal format
        try:
            return float(degree_str)
        except:
            return None

def format_coordinate_for_polygon(coord):
    """
    Convert decimal coordinate to the specific format required for polygon
    Maximum 8 digits as per requirement
    """
    if coord is None:
        return None
    
    # Convert to the required format and ensure max 8 digits
    formatted = round(float(coord) * (10 ** 7))
    
    # Convert to string and limit to 8 digits
    coord_str = str(abs(formatted))
    if len(coord_str) > 8:
        coord_str = coord_str[:8]
    
    # Convert back to int and restore sign
    result = int(coord_str)
    if coord < 0:  # Use original coord sign, not formatted
        result = -result
        
    return result

def generate_polygon_command(row):
    """
    Generate the polygon command for a single row
    Based on CIQ_LTE.xlsx format where:
    - Corner X columns contain latitude values
    - Unnamed: Y columns contain longitude values (paired with Corner columns)
    """
    cell_id = row['EutranCellFDDId']
    corners = []
    
    # Define the mapping between Corner columns and their corresponding Unnamed longitude columns
    corner_mappings = [
        ('Corner 1', 'Unnamed: 4'),
        ('Corner 2', 'Unnamed: 6'), 
        ('Corner 3', 'Unnamed: 8'),
        ('Corner 4', 'Unnamed: 10'),
        ('Corner 5', 'Unnamed: 12'),
        ('Corner 6', 'Unnamed: 14'),
        ('Corner 7', 'Unnamed: 16'),
        ('Corner 8', 'Unnamed: 18'),
        ('Corner 9', 'Unnamed: 20'),
        ('Corner 10', 'Unnamed: 22'),
        ('Corner 11', 'Unnamed: 24'),
        ('Corner 12', 'Unnamed: 26'),
        ('Corner 13', 'Unnamed: 28'),
        ('Corner 14', 'Unnamed: 30'),
        ('Corner 15', 'Unnamed: 32')
    ]
    
    for lat_col, lon_col in corner_mappings:
        if lat_col in row.index and lon_col in row.index:
            lat_degree = row[lat_col]
            lon_degree = row[lon_col]
            
            if pd.notna(lat_degree) and pd.notna(lon_degree) and lat_degree != '' and lon_degree != '':
                # Convert to decimal
                lat_decimal = convert_degree_to_decimal(lat_degree)
                lon_decimal = convert_degree_to_decimal(lon_degree)
                
                if lat_decimal is not None and lon_decimal is not None:
                    # For North American coordinates, longitude should typically be negative
                    # If longitude is positive and appears to be North American (typical range), make it negative
                    if lon_decimal > 0 and 60 <= lon_decimal <= 180:
                        lon_decimal = -lon_decimal
                    
                    # Format for polygon using the specified calculation
                    lat_formatted = format_coordinate_for_polygon(lat_decimal)
                    lon_formatted = format_coordinate_for_polygon(lon_decimal)
                    
                    corners.append(f"cornerLatitude={lat_formatted},cornerLongitude={lon_formatted}")
    
    if corners:
        corner_string = ";".join(corners)
        return f"set EUtranCellFDD={cell_id} eutranCellPolygon {corner_string};"
    else:
        return f"# No valid corners found for {cell_id}"

def load_excel_and_convert(file_path):
    """
    Load the Excel file and convert to polygon commands
    """
    try:
        # Read the specific sheet that contains polygon data
        polygon_data = pd.read_excel(file_path, sheet_name='eUtranCellPolygon')
        
        if 'EutranCellFDDId' not in polygon_data.columns:
            return None, "EutranCellFDDId column not found in eUtranCellPolygon sheet"
        
        # Generate polygon commands
        commands = []
        for idx, row in polygon_data.iterrows():
            if pd.notna(row['EutranCellFDDId']) and row['EutranCellFDDId'] != '':
                command = generate_polygon_command(row)
                commands.append(command)
        
        return commands, f"Successfully processed {len(commands)} cells from eUtranCellPolygon sheet"
        
    except Exception as e:
        return None, f"Error reading Excel file: {str(e)}"

# Streamlit App Interface
def main():
    st.title("CIQ LTE Polygon Converter")
    st.write("Convert CIQ_LTE.xlsx polygon data to MO command format")
    
    # Step 1: Upload the Excel File
    uploaded_file = st.file_uploader("Upload CIQ_LTE.xlsx File", type=["xlsx"])
    
    if uploaded_file:
        # Load and convert the data
        commands, message = load_excel_and_convert(uploaded_file)
        
        st.info(message)
        
        if commands:
            # Display the results
            st.subheader("Generated Polygon Commands")
            
            # Show first few commands as preview
            st.write("**Preview (first 5 commands):**")
            for i, cmd in enumerate(commands[:5]):
                st.code(cmd)
            
            if len(commands) > 5:
                st.write(f"... and {len(commands) - 5} more commands")
            
            # Prepare download content
            download_content = "\n".join(commands)
            
            # Download button
            st.download_button(
                label="Download All Polygon Commands",
                data=download_content,
                file_name="polygon_commands.txt",
                mime="text/plain"
            )
            
            # Show column information for debugging
            with st.expander("Debug: Show detected columns"):
                try:
                    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
                    for sheet_name, df in excel_data.items():
                        if 'EutranCellFDDId' in df.columns:
                            st.write(f"**Sheet: {sheet_name}**")
                            st.write("Columns:", list(df.columns))
                            corner_cols = [col for col in df.columns if 'corner' in col.lower() or 'latitude' in col.lower() or 'longitude' in col.lower()]
                            st.write("Corner-related columns:", corner_cols)
                            
                            # Show sample data
                            if len(df) > 0:
                                st.write("Sample row:")
                                st.write(df.iloc[0][['EutranCellFDDId'] + corner_cols[:4]].to_dict())
                            break
                except Exception as e:
                    st.error(f"Error showing debug info: {e}")

if __name__ == "__main__":
    main()
