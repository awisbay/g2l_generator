import pandas as pd
import streamlit as st
import zipfile
import io

# Step 1: Read the Excel file
#@st.cache
def load_excel(file):
    return pd.read_excel(file, sheet_name=None)  # Read all sheets into a dictionary

def format_coordinates(coord):
    """
    Takes a coordinate (latitude or longitude) and converts it into an 8-digit format.
    The number will be rounded up or down based on the last digit.
    """
    # Remove the decimal point and take the first 8 digits
    coord_str = str(abs(coord)).replace(".", "")[:8]

    # Convert the result back to an integer, rounding appropriately
    formatted_coord = round(float(coord_str) * (10 ** -7))  # Divide by 10^7 to scale it down to the desired precision
    if coord < 0:
        formatted_coord = -formatted_coord  # Maintain negative sign for longitude

    return formatted_coord

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

# Step 5: Create ZIP file with all generated XML files
def create_zip_file(lnr_function_xml, lte_cells_xml, cell_add_mo_xml, mo_function_xml, feature_activation_xml, enbname):
    """
    Create a ZIP file containing all generated XML files
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add each XML file to the zip
        zip_file.writestr(f"09_{enbname}_MO_Function.xml", mo_function_xml)
        zip_file.writestr(f"08_{enbname}_LNR_Function.xml", lnr_function_xml)
        zip_file.writestr(f"12_{enbname}_FeatureActivation.xml", feature_activation_xml)
        zip_file.writestr(f"10_{enbname}_LTE_Cells.xml", lte_cells_xml)
        zip_file.writestr(f"11_{enbname}_Cell_Add_MO.xml", cell_add_mo_xml)
    
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
            with open("/Users/wisbay/Documents/ypndev/g2l_generator/03_MO_Function.xml", 'r') as f:
                mo_function_xml = f.read()
                
            with open("/Users/wisbay/Documents/ypndev/g2l_generator/04_LNR_Function.xml", 'r') as f:
                lnr_template = f.read()
                
            with open("/Users/wisbay/Documents/ypndev/g2l_generator/08_FeatureActivation.xml", 'r') as f:
                feature_activation_xml = f.read()
            
            with open("/Users/wisbay/Documents/ypndev/g2l_generator/LTE_Cells_Template.xml", 'r') as f:
                lte_cells_template = f.read()
                
            with open("/Users/wisbay/Documents/ypndev/g2l_generator/05_Cell_Add_MO_Template.xml", 'r') as f:
                cell_add_mo_template = f.read()

            # Step 3: Generate XML files based on the enbname
            lnr_function_xml = generate_lnr_function_xml(enbname, excel_data, lnr_template)
            lte_cells_xml = generate_lte_cells_xml(excel_data, enbname, lte_cells_template)
            cell_add_mo_xml = generate_cell_add_mo_xml(excel_data, enbname, cell_add_mo_template)

            # Step 4: Display or download the generated XML files
            #st.subheader("Generated 04_LNR_Function.xml")
            #st.text_area("04_LNR_Function.xml", lnr_function_xml, height=400)

            #st.subheader("Generated LTE_Cells_template.xml")
            #st.text_area("LTE_Cells_template.xml", lte_cells_xml, height=400)

            # Create ZIP file with all XML files
            zip_data = create_zip_file(lnr_function_xml, lte_cells_xml, cell_add_mo_xml, mo_function_xml, feature_activation_xml, enbname)

            # Option to download individual XML files
            # Option to download all files as ZIP
            st.subheader("Download All Files:")
            st.download_button(
                "Download All XML Files (ZIP)", 
                zip_data, 
                f"{enbname}_XML_Files.zip",
                mime="application/zip"
            )

if __name__ == "__main__":
    main()
