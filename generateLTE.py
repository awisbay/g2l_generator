import pandas as pd
import streamlit as st
import zipfile
import io
import re

# Step 1: Read the Excel file
#@st.cache
def load_excel(file):
    return pd.read_excel(file, sheet_name=None)  # Read all sheets into a dictionary

def format_coordinates(coord):
    """
    Takes a coordinate (latitude or longitude) and converts it into an 8-digit format.
    Maximum 8 digits as per requirement.
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

# Step 2: Generate XML for 04_LNR_Function.xml
def generate_lnr_function_xml(enbname, excel_data, template_xml):
    # Get the relevant sheet data
    sheet_data = excel_data['eUtran Parameters']  # Assuming 'eUtran Parameters' contains the enbname and eNBId
    cluster_data = excel_data['Cluster']  # 'cluster' sheet contains the FDN value

    # Find the corresponding eNBId for the provided enbname
    enb_id = sheet_data[sheet_data['eNBName'] == enbname]['eNBId'].values

    if len(enb_id) == 0:
        # If enbname doesn't exist, return an error message or handle as needed
        return f"Error: eNB name '{enbname}' not found."
    
    enb_id = enb_id[0]  # Assuming only one match for enbname
    
    # Get the FDN value from the 'Cluster' sheet based on matching eNodeB Name
    fdn_row = cluster_data[cluster_data['eNodeB Name'] == enbname]
    if len(fdn_row) == 0:
        # If enbname doesn't exist in Cluster sheet, handle this case
        fdn_value = f"Error: eNB name '{enbname}' not found in Cluster sheet."
    else:
        fdn_original = fdn_row['FDN'].values[0]  # Get the FDN value for this specific eNB
        # Transform FDN: remove ",ManagedElement=..." part and clean up spaces
        # Split by comma and filter out ManagedElement parts
        fdn_parts = fdn_original.split(',')
        filtered_parts = [part.strip() for part in fdn_parts if not part.strip().startswith('ManagedElement=')]
        fdn_value = ','.join(filtered_parts)
    
    # Replace the placeholders with actual data
    xml_data = template_xml.replace("{enbid}", str(enb_id))  # Replace {enbid} with the actual eNBId
    xml_data = xml_data.replace("{FDN}", fdn_value)  # Replace {FDN} with the transformed FDN value
    return xml_data

# Step 3: Generate LTE_Cells_template.xml
def generate_lte_cells_xml(excel_data, enbname, template_xml):
    # Get the relevant sheet data
    sheet_data = excel_data['eUtran Parameters']  # Assuming 'eUtran Parameters' contains the cells data
    pci_data = excel_data['PCI']  # Assuming 'PCI' sheet contains the additional parameters
    enb_info_data = excel_data['eNB Info']  # 'eNB Info' sheet contains the tac value

    # Filter rows from the 'eUtran Parameters' sheet that match the enbname
    cell_data = sheet_data[sheet_data['eNBName'] == enbname]

    # Merge PCI data based on EutranCellFDDId
    merged_data = pd.merge(cell_data, pci_data[['EutranCellFDDId', 'rachRootSequence', 'cellId', 'sectorId', 'PhysicalLayerCellIdGroup', 'physicalLayerSubCellId']], on='EutranCellFDDId', how='left')

    # Get the TAC value from the 'eNB Info' sheet based on eNBname
    tac = enb_info_data[enb_info_data['eNodeB Name'] == enbname]['tac'].values
    if len(tac) == 0:
        # If eNBname doesn't exist in 'eNB Info', handle this case
        tac_value = "Error: eNB name '{enbname}' not found in eNB Info sheet."
    else:
        tac_value = tac[0]  # Assuming only one match for eNBname

    # Generate XML for each row
    cell_xml_data = []
    for idx, row in merged_data.iterrows():
        cell_xml = template_xml

        latitude = format_coordinates(row['latitude'])
        longitude = format_coordinates(row['longitude'])
        
        # Replace the placeholders with actual data from the merged data
        cell_xml = cell_xml.replace("{EutranCellFDDId}", str(row['EutranCellFDDId']))
        cell_xml = cell_xml.replace("{AUG}", str(row['sectorId']))  # Use sectorId from PCI sheet
        cell_xml = cell_xml.replace("{configuredMaxTxPower}", str(row['configuredMaxTxPower']))
        cell_xml = cell_xml.replace("{rachRootSequence}", str(row['rachRootSequence']))  
        cell_xml = cell_xml.replace("{cellId}", str(row['cellId'])) 
        cell_xml = cell_xml.replace("{latitude}", str(latitude))
        cell_xml = cell_xml.replace("{longitude}", str(longitude))
        cell_xml = cell_xml.replace("{cellRange}", str(row['cellRange']))
        cell_xml = cell_xml.replace("{earfcnDl}", str(row['earfcnDl']))
        cell_xml = cell_xml.replace("{earfcnUl}", str(row['earfcnUl']))
        cell_xml = cell_xml.replace("{dlChannelBandwidth}", str(row['dlChannelBandwidth']))
        cell_xml = cell_xml.replace("{qRxLevMin}", str(row['qRxLevMin']))
        cell_xml = cell_xml.replace("{PhysicalLayerCellIdGroup}", str(row['PhysicalLayerCellIdGroup']))
        cell_xml = cell_xml.replace("{physicalLayerSubCellId}", str(row['physicalLayerSubCellId']))
         #  # Use cellId from PCI sheet
        
        # Replace the {tac} placeholder with the value from the 'eNB Info' sheet
        cell_xml = cell_xml.replace("{tac}", str(tac_value))
        
        cell_xml_data.append(cell_xml)

    return "\n".join(cell_xml_data)

# Step 4: Generate 05_Cell_Add_MO.xml  
def generate_cell_add_mo_xml(excel_data, enbname, template_xml):
    # Get the relevant sheet data
    sheet_data = excel_data['eUtran Parameters']  # Assuming 'eUtran Parameters' contains the cells data

    # Filter rows from the 'eUtran Parameters' sheet that match the enbname
    cell_data = sheet_data[sheet_data['eNBName'] == enbname]

    # Generate XML for each row
    cell_xml_data = []
    for idx, row in cell_data.iterrows():
        cell_xml = template_xml
        
        # Replace the placeholder {EutranCellFDDId} with actual data
        cell_xml = cell_xml.replace("{EutranCellFDDId}", str(row['EutranCellFDDId']))
        
        cell_xml_data.append(cell_xml)

    return "\n".join(cell_xml_data)

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
                    lat_formatted = format_coordinates(lat_decimal)
                    lon_formatted = format_coordinates(lon_decimal)
                    
                    corners.append(f"cornerLatitude={lat_formatted},cornerLongitude={lon_formatted}")
    
    if corners:
        corner_string = ";".join(corners)
        return f"set EUtranCellFDD={cell_id} eutranCellPolygon {corner_string};"
    else:
        return f"# No valid corners found for {cell_id}"

def generate_polygon_mos_file(excel_data, enbname):
    """
    Generate the polygon and coverage .mos file content for the specified eNB
    """
    try:
        polygon_commands = []
        coverage_commands = []
        
        # Generate polygon commands
        if 'eUtranCellPolygon' in excel_data:
            polygon_data = excel_data['eUtranCellPolygon']
            
            if 'EutranCellFDDId' in polygon_data.columns:
                # Detect the correct column mapping for this file
                column_mappings = detect_polygon_column_mapping(polygon_data)
                
                # Filter polygon data for the specified eNB
                if 'eUtran Parameters' in excel_data:
                    enb_cells = excel_data['eUtran Parameters'][excel_data['eUtran Parameters']['eNBName'] == enbname]['EutranCellFDDId'].values
                    filtered_polygon_data = polygon_data[polygon_data['EutranCellFDDId'].isin(enb_cells)]
                else:
                    # If no eUtran Parameters sheet, try to filter by eNBName in polygon sheet
                    if 'eNBName' in polygon_data.columns:
                        filtered_polygon_data = polygon_data[polygon_data['eNBName'] == enbname]
                    else:
                        filtered_polygon_data = polygon_data
                
                # Generate polygon commands
                for idx, row in filtered_polygon_data.iterrows():
                    if pd.notna(row['EutranCellFDDId']) and row['EutranCellFDDId'] != '':
                        command = generate_polygon_command(row, column_mappings)
                        polygon_commands.append(command)
        
        # Generate coverage commands
        coverage_commands = generate_coverage_commands(excel_data, enbname)
        
        # If no commands generated, return None
        if not polygon_commands and not coverage_commands:
            return None
        
        # Create the .mos file content with proper header and footer
        content_sections = []
        
        if polygon_commands:
            content_sections.append(chr(10).join(polygon_commands))
        
        if coverage_commands:
            if polygon_commands:
                content_sections.append("")  # Add empty line between sections
            content_sections.append(chr(10).join(coverage_commands))
        
        mos_content = f"""# ------------------------------------
# Generate by: XML Generator for eNB Configuration
# eNB Name: {enbname}
# ------------------------------------

l mkdir $nodename_Polygon_Coverage_Log
$timeCheck = `date "+%y%m%d_%H%M%S"`
l+ $nodename_Polygon_Coverage_Log/$nodename_LTE_Polygon_$timeCheck.log

confb+
gs+
alt

{chr(10).join(content_sections)}


alt
confb-
gs-
l-"""
        
        return mos_content
        
    except Exception as e:
        return None

def generate_coverage_commands(excel_data, enbname):
    """
    Generate coverage commands for the specified eNB from eUtranCellCoverage sheet
    """
    try:
        # Check if eUtranCellCoverage sheet exists
        if 'eUtranCellCoverage' not in excel_data:
            return []
            
        coverage_data = excel_data['eUtranCellCoverage']
        
        if 'EutranCellFDDId' not in coverage_data.columns:
            return []
        
        # Filter coverage data for the specified eNB
        # Get cell IDs for this eNB from eUtran Parameters sheet
        if 'eUtran Parameters' in excel_data:
            enb_cells = excel_data['eUtran Parameters'][excel_data['eUtran Parameters']['eNBName'] == enbname]['EutranCellFDDId'].values
            filtered_coverage_data = coverage_data[coverage_data['EutranCellFDDId'].isin(enb_cells)]
        else:
            # If no eUtran Parameters sheet, try to filter by eNBName in coverage sheet
            if 'eNBName' in coverage_data.columns:
                filtered_coverage_data = coverage_data[coverage_data['eNBName'] == enbname]
            else:
                filtered_coverage_data = coverage_data
        
        if len(filtered_coverage_data) == 0:
            return []
        
        # Generate coverage commands
        commands = []
        for idx, row in filtered_coverage_data.iterrows():
            if pd.notna(row['EutranCellFDDId']) and row['EutranCellFDDId'] != '':
                cell_id = row['EutranCellFDDId']
                
                # Get coverage parameters with defaults if missing
                pos_cell_bearing = row.get('posCellBearing', 0) if pd.notna(row.get('posCellBearing')) else 0
                pos_cell_opening_angle = row.get('posCellOpeningAngle', 1200) if pd.notna(row.get('posCellOpeningAngle')) else 1200
                pos_cell_radius = row.get('posCellRadius', 15000) if pd.notna(row.get('posCellRadius')) else 15000
                
                # Convert to integers
                pos_cell_bearing = int(float(pos_cell_bearing))
                pos_cell_opening_angle = int(float(pos_cell_opening_angle))
                pos_cell_radius = int(float(pos_cell_radius))
                
                command = f"set EutranCellFDD={cell_id} eutranCellCoverage posCellBearing={pos_cell_bearing},posCellOpeningAngle={pos_cell_opening_angle},posCellRadius={pos_cell_radius}"
                commands.append(command)
        
        return commands
        
    except Exception as e:
        return []

# Smart column detection function
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

# Step 5: Create ZIP file with all generated XML files
def create_zip_file(lnr_function_xml, lte_cells_xml, cell_add_mo_xml, mo_function_xml, feature_activation_xml, polygon_mos, enbname):
    """
    Create a ZIP file containing all generated XML files and polygon .mos file
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add each XML file to the zip
        zip_file.writestr(f"09_{enbname}_MO_Function.xml", mo_function_xml)
        zip_file.writestr(f"08_{enbname}_LNR_Function.xml", lnr_function_xml)
        zip_file.writestr(f"12_{enbname}_FeatureActivation.xml", feature_activation_xml)
        zip_file.writestr(f"10_{enbname}_LTE_Cells.xml", lte_cells_xml)
        zip_file.writestr(f"11_{enbname}_Cell_Add_MO.xml", cell_add_mo_xml)
        
        # Add polygon .mos file if available
        if polygon_mos:
            zip_file.writestr(f"13_{enbname}_Polygon.mos", polygon_mos)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# Streamlit App Interface
def main():
    st.title("XML Generator for eNB Configuration")
    
    # Step 1: Upload the Excel File
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    
    if uploaded_file:
        excel_data = load_excel(uploaded_file)
        
        # Step 2: Input enbname
        enbname = st.text_input("Enter eNB Name:")
        
        if enbname:
            # Load the templates for the XML files
            with open("/var/www/irsmigration/03_MO_Function.xml", 'r') as f:
                mo_function_xml = f.read()
                
            with open("/var/www/irsmigration/04_LNR_Function.xml", 'r') as f:
                lnr_template = f.read()
                
            with open("/var/www/irsmigration/08_FeatureActivation.xml", 'r') as f:
                feature_activation_xml = f.read()
            
            with open("/var/www/irsmigration/LTE_Cells_Template.xml", 'r') as f:
                lte_cells_template = f.read()
                
            with open("/var/www/irsmigration/05_Cell_Add_MO_Template.xml", 'r') as f:
                cell_add_mo_template = f.read()

            # Step 3: Generate XML files based on the enbname
            lnr_function_xml = generate_lnr_function_xml(enbname, excel_data, lnr_template)
            lte_cells_xml = generate_lte_cells_xml(excel_data, enbname, lte_cells_template)
            cell_add_mo_xml = generate_cell_add_mo_xml(excel_data, enbname, cell_add_mo_template)

            # Generate polygon .mos file content
            polygon_mos_content = generate_polygon_mos_file(excel_data, enbname)

            # Step 4: Display or download the generated XML files
            #st.subheader("Generated 04_LNR_Function.xml")
            #st.text_area("04_LNR_Function.xml", lnr_function_xml, height=400)

            #st.subheader("Generated LTE_Cells_template.xml")
            #st.text_area("LTE_Cells_template.xml", lte_cells_xml, height=400)

            # Show polygon and coverage status
            if polygon_mos_content:
                st.success(f"✅ Polygon & Coverage file generated: 13_{enbname}_Polygon.mos")
            else:
                st.warning("⚠️ No polygon or coverage data found in Excel file")

            # Create ZIP file with all XML files and polygon .mos file
            zip_data = create_zip_file(lnr_function_xml, lte_cells_xml, cell_add_mo_xml, mo_function_xml, feature_activation_xml, polygon_mos_content, enbname)

            # Option to download individual XML files
            # Option to download all files as ZIP
            st.subheader("Download All Files:")
            file_count = 5 + (1 if polygon_mos_content else 0)
            st.download_button(
                f"Download All Files (ZIP) - {file_count} files", 
                zip_data, 
                f"{enbname}_LTE_Script.zip",
                mime="application/zip"
            )

if __name__ == "__main__":
    main()
