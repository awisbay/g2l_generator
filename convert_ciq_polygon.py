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

def generate_polygon_command(row, column_mappings=None):
    """
    Generate the polygon command for a single row
    Based on CIQ_LTE.xlsx format where:
    - Corner X columns contain latitude values
    - Unnamed: Y columns contain longitude values (paired with Corner columns)
    """
    cell_id = row['EutranCellFDDId']
    corners = []
    
    # Use provided mappings or default mappings
    if column_mappings is None:
        corner_mappings = [
            ('Corner 1', 'Unnamed: 3'),
            ('Corner 2', 'Unnamed: 5'), 
            ('Corner 3', 'Unnamed: 7'),
            ('Corner 4', 'Unnamed: 9'),
            ('Corner 5', 'Unnamed: 11'),
            ('Corner 6', 'Unnamed: 13'),
            ('Corner 7', 'Unnamed: 15'),
            ('Corner 8', 'Unnamed: 17'),
            ('Corner 9', 'Unnamed: 19'),
            ('Corner 10', 'Unnamed: 21'),
            ('Corner 11', 'Unnamed: 23'),
            ('Corner 12', 'Unnamed: 25'),
            ('Corner 13', 'Unnamed: 27'),
            ('Corner 14', 'Unnamed: 29'),
            ('Corner 15', 'Unnamed: 31')
        ]
    else:
        corner_mappings = column_mappings
    
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

def generate_coverage_command(row):
    """
    Generate coverage command for a single row from eUtranCellCoverage sheet
    """
    cell_id = row['EutranCellFDDId']
    
    # Get coverage parameters with defaults if missing
    pos_cell_bearing = row.get('posCellBearing', 0) if pd.notna(row.get('posCellBearing')) else 0
    pos_cell_opening_angle = row.get('posCellOpeningAngle', 1200) if pd.notna(row.get('posCellOpeningAngle')) else 1200
    pos_cell_radius = row.get('posCellRadius', 15000) if pd.notna(row.get('posCellRadius')) else 15000
    
    # Convert to integers
    pos_cell_bearing = int(float(pos_cell_bearing))
    pos_cell_opening_angle = int(float(pos_cell_opening_angle))
    pos_cell_radius = int(float(pos_cell_radius))
    
    return f"set EutranCellFDD={cell_id} eutranCellCoverage posCellBearing={pos_cell_bearing},posCellOpeningAngle={pos_cell_opening_angle},posCellRadius={pos_cell_radius}"

def load_excel_and_convert(file_path):
    """
    Load the Excel file and convert to polygon commands
    """
    try:
        # Read the specific sheet that contains polygon data
        polygon_data = pd.read_excel(file_path, sheet_name='eUtranCellPolygon')
        
        if 'EutranCellFDDId' not in polygon_data.columns:
            return None, "EutranCellFDDId column not found in eUtranCellPolygon sheet"
        
        # Detect the correct column mapping for this file
        column_mappings = detect_polygon_column_mapping(polygon_data)
        
        # Generate polygon commands
        commands = []
        for idx, row in polygon_data.iterrows():
            if pd.notna(row['EutranCellFDDId']) and row['EutranCellFDDId'] != '':
                command = generate_polygon_command(row, column_mappings)
                commands.append(command)
        
        return commands, f"Successfully processed {len(commands)} cells from eUtranCellPolygon sheet"
        
    except Exception as e:
        return None, f"Error reading Excel file: {str(e)}"

def load_excel_and_convert_coverage(file_path):
    """
    Load the Excel file and convert to coverage commands
    """
    try:
        # Read the specific sheet that contains coverage data
        coverage_data = pd.read_excel(file_path, sheet_name='eUtranCellCoverage')
        
        if 'EutranCellFDDId' not in coverage_data.columns:
            return None, "EutranCellFDDId column not found in eUtranCellCoverage sheet"
        
        # Generate coverage commands
        commands = []
        for idx, row in coverage_data.iterrows():
            if pd.notna(row['EutranCellFDDId']) and row['EutranCellFDDId'] != '':
                command = generate_coverage_command(row)
                commands.append(command)
        
        return commands, f"Successfully processed {len(commands)} cells from eUtranCellCoverage sheet"
        
    except Exception as e:
        return None, f"Error reading Excel file: {str(e)}"

def detect_polygon_column_mapping(polygon_data):
    """
    Detect the correct column mapping for polygon data based on the actual columns in the file
    """
    columns = list(polygon_data.columns)
    mappings = []
    
    # Look for Corner columns and their corresponding Unnamed columns
    for i in range(1, 16):  # Check up to 15 corners
        corner_col = f'Corner {i}'
        if corner_col in columns:
            corner_idx = columns.index(corner_col)
            
            # The longitude column should be the very next column after Corner
            # and it should be an Unnamed column
            if corner_idx + 1 < len(columns) and columns[corner_idx + 1].startswith('Unnamed:'):
                lon_col = columns[corner_idx + 1]
                mappings.append((corner_col, lon_col))
    
    return mappings

# Streamlit App Interface
def main():
    st.title("CIQ LTE Polygon & Coverage Converter")
    st.write("Convert CIQ_LTE.xlsx polygon and coverage data to MO command format")
    
    # Step 1: Upload the Excel File
    uploaded_file = st.file_uploader("Upload CIQ_LTE.xlsx File", type=["xlsx"])
    
    if uploaded_file:
        # Check available sheets
        try:
            excel_data = pd.read_excel(uploaded_file, sheet_name=None)
            available_sheets = list(excel_data.keys())
            st.info(f"Available sheets: {', '.join(available_sheets)}")
        except:
            st.error("Error reading Excel file")
            return
        
        # Process polygon data
        polygon_commands = None
        polygon_message = None
        if 'eUtranCellPolygon' in available_sheets:
            polygon_commands, polygon_message = load_excel_and_convert(uploaded_file)
        
        # Process coverage data  
        coverage_commands = None
        coverage_message = None
        if 'eUtranCellCoverage' in available_sheets:
            coverage_commands, coverage_message = load_excel_and_convert_coverage(uploaded_file)
        
        # Display results
        if polygon_commands or coverage_commands:
            all_commands = []
            
            if polygon_commands:
                st.success(polygon_message)
                st.subheader("Generated Polygon Commands")
                st.write("**Preview (first 3 polygon commands):**")
                for i, cmd in enumerate(polygon_commands[:3]):
                    st.code(cmd)
                if len(polygon_commands) > 3:
                    st.write(f"... and {len(polygon_commands) - 3} more polygon commands")
                all_commands.extend(polygon_commands)
            
            if coverage_commands:
                st.success(coverage_message)
                st.subheader("Generated Coverage Commands")
                st.write("**Preview (first 3 coverage commands):**")
                for i, cmd in enumerate(coverage_commands[:3]):
                    st.code(cmd)
                if len(coverage_commands) > 3:
                    st.write(f"... and {len(coverage_commands) - 3} more coverage commands")
                if polygon_commands:
                    all_commands.append("")  # Add empty line between sections
                all_commands.extend(coverage_commands)
            
            # Prepare download content
            download_content = "\n".join(all_commands)
            
            # Download button
            st.download_button(
                label="Download All Commands",
                data=download_content,
                file_name="polygon_coverage_commands.txt",
                mime="text/plain"
            )
        else:
            if not polygon_commands and 'eUtranCellPolygon' in available_sheets:
                st.error(polygon_message)
            if not coverage_commands and 'eUtranCellCoverage' in available_sheets:
                st.error(coverage_message)
            if 'eUtranCellPolygon' not in available_sheets and 'eUtranCellCoverage' not in available_sheets:
                st.warning("No eUtranCellPolygon or eUtranCellCoverage sheets found in the uploaded file")
        
        # Show column information for debugging
        with st.expander("Debug: Show detected columns"):
            try:
                for sheet_name, df in excel_data.items():
                    if sheet_name in ['eUtranCellPolygon', 'eUtranCellCoverage']:
                        st.write(f"**Sheet: {sheet_name}**")
                        st.write("Columns:", list(df.columns))
                        
                        if sheet_name == 'eUtranCellPolygon':
                            corner_cols = [col for col in df.columns if 'corner' in col.lower() or 'latitude' in col.lower() or 'longitude' in col.lower()]
                            st.write("Corner-related columns:", corner_cols)
                        elif sheet_name == 'eUtranCellCoverage':
                            coverage_cols = [col for col in df.columns if any(x in col.lower() for x in ['bearing', 'angle', 'radius'])]
                            st.write("Coverage-related columns:", coverage_cols)
                        
                        # Show sample data
                        if len(df) > 0:
                            st.write("Sample row:")
                            relevant_cols = ['EutranCellFDDId']
                            if sheet_name == 'eUtranCellPolygon':
                                relevant_cols.extend([col for col in df.columns if 'Corner' in col][:4])
                            elif sheet_name == 'eUtranCellCoverage':
                                relevant_cols.extend(['posCellBearing', 'posCellOpeningAngle', 'posCellRadius'])
                            
                            sample_data = {}
                            for col in relevant_cols:
                                if col in df.columns:
                                    sample_data[col] = df.iloc[0][col]
                            st.write(sample_data)
            except Exception as e:
                st.error(f"Error showing debug info: {e}")
        
        # Load and convert coverage data if available
        coverage_commands, coverage_message = load_excel_and_convert_coverage(uploaded_file)
        
        st.info(coverage_message)
        
        if coverage_commands:
            # Display the results
            st.subheader("Generated Coverage Commands")
            
            # Show first few commands as preview
            st.write("**Preview (first 5 commands):**")
            for i, cmd in enumerate(coverage_commands[:5]):
                st.code(cmd)
            
            if len(coverage_commands) > 5:
                st.write(f"... and {len(coverage_commands) - 5} more commands")
            
            # Prepare download content
            download_content = "\n".join(coverage_commands)
            
            # Download button
            st.download_button(
                label="Download All Coverage Commands",
                data=download_content,
                file_name="coverage_commands.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
