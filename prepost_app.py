import pandas as pd

# Load Excel file and read 'target_cells' sheet
file_path = 'MD-QC-BSC-Template-20220622_102727.xlsx'
df = pd.read_excel(file_path, sheet_name='target_cells')

# Extract relevant columns
def posthc_newbsc(df):
    bsc_new_list = df['BSC_NEW'].tolist()
    cell_list = df['CELL'].tolist()
    rxstg_new_list = df['RXSTG_NEW'].tolist()
    row_length = len(df)
    # Generate script lines
    script_lines = []

    section = f"""@SET {{N}}=1
@LABEL PRINT                                 
@GETDATE {{DATE}} -DDMMYY-
@GETTIME {{TIME}} -HHMM
@GETDAY {{DAY}} SUN MON TUE WED THU FRI SAT
@SET {{D}}="S:\\vendor_ericsson\\IRS\\Guan\\2G\\NB17042025\\POST-RXSTG-"
@@LOG FILE NAME
    """
    for i, cell in enumerate(cell_list, start=1):
        line_st = f'@IF {{N}} = {i}   THEN @SET {{S}} ="{cell}"+{{DATE}}+{{DAY}}+{{TIME}}+.log" \n'    
        section += line_st

    section += "@@BSC \n"

    for i, bsc in enumerate(bsc_new_list, start=1):
        line_bsc = f'@IF {{N}} = {i}   THEN @SET {{BSC}} ="{bsc}" \n'    
        section += line_bsc

    section += "@@ TG \n"

    for i, rxstg in enumerate(rxstg_new_list, start=1):
        line_tg = f'@IF {{N}} = {i}   THEN @SET {{TG}} =RXSTG-{rxstg}\n'
        section += line_tg

    section += "@@ CELL ID \n"

    for i, cell in enumerate(cell_list, start=1):
        line_cell = f'@IF {{N}} = {i}  THEN @SET {{CELL}} = {cell}" \n'    
        section += line_cell

    section += f"""
@T 1 
@LOG ON {{D}}{{S}} 
RXMOP:MO={{TG}}; 
@RITEM {{TRM}} {{_LINE8}} " " 0
RXCDP:MO={{TG}}; 
RXTCP:MO={{TG}}; 
@LABEL RLDEP
RLDEP:CELL={{CELL}};
RLCCP:CELL={{CELL}};
RLCPP:CELL={{CELL}};
RLBCP:CELL={{CELL}};
RLSLP:CELL={{CELL}};
RLIHP:CELL={{CELL}};
RLLCP:CELL={{CELL}};
RLIMP:CELL={{CELL}};
RLHPP:CELL={{CELL}};
RLPCP:CELL={{CELL}};
RLAPP:CELL={{CELL}};
RLSSP:CELL={{CELL}};
RLLOP:CELL={{CELL}};
RLCXP:CELL={{CELL}};
RLLDP:CELL={{CELL}};
RLLPP:CELL={{CELL}};
RLSBP:CELL={{CELL}};
RLSUP:CELL={{CELL}};
RLLHP:CELL={{CELL}};
RLACP:CELL={{CELL}};
RLGSP:CELL={{CELL}};
RLDHP:CELL={{CELL}};
RLDUP:CELL={{CELL}};
RLDGP:CELL={{CELL}};
RLCHP:CELL={{CELL}};
RLCFP:CELL={{CELL}};
RLBDP:CELL={{CELL}};
RLDTP:CELL={{CELL}};
RLUMP:CELL={{CELL}};
RLMFP:CELL={{CELL}};
RLLFP:CELL={{CELL}};
RLPDP:CELL={{CELL}};
RLGAP:CELL={{CELL}};
RLLUP:CELL={{CELL}};
RLDMP:CELL={{CELL}};
RLSRP:CELL={{CELL}};
RLCDP:CELL={{CELL}};
RLSMP:CELL={{CELL}};
RLCLP:CELL={{CELL}};
RLCSP:CELL={{CELL}};
RLPBP:CELL={{CELL}};
RLDEP:CELL={{CELL}}; 
RLCFP:CELL={{CELL}}; 
RLBDP:CELL={{CELL}}; 
RLCRP:CELL={{CELL}}; 
RLGSP:CELL={{CELL}}; 
RLGRP:CELL={{CELL}}; 
RLLOP:CELL={{CELL}}; 
RLCPP:CELL={{CELL}}; 
RLSLP:CELL={{CELL}}; 
RLCHP:CELL={{CELL}};  
RLCCP:CELL={{CELL}}; 
RLSTP:CELL={{CELL}}; 
RLSBP:CELL={{CELL}}; 
RLNRP:CELL={{CELL}},CELLR=ALL,NODATA;
RLNRP:CELL={{CELL}},CELLR=ALL,UTRAN;    
@LABEL RXMFP
RXMOP:MO={{TG}},SUBORD;
RXMFP:MO={{TG}},SUBORD;
RXMFP:MO={{TG}},SUBORD,FAULTY; 
RXMSP:MO={{TG}},SUBORD;
RXASP:MO={{TG}};
RXAPP:MO={{TG}};
RXTCP:MO={{TG}};
RXCDP:MO={{TG}}; 
CACLP;    
@LOG OFF 
@T 1 
@INC {{N}} 1 
@IF {{N}} <= {row_length} THEN GOTO PRINT
@LABEL STOP
    """
    script_lines.append(section)

    # Join all lines into one string with newlines
    script_output = "\n".join(script_lines)

    return script_output

def prehc_oldbsc(df):
    bsc_new_list = df['BSC_NEW'].tolist()
    cell_list = df['CELL'].tolist()
    rxstg_new_list = df['RXSTG_NEW'].tolist()
    row_length = len(df)
    # Generate script lines
    script_lines = []

    section = f"""@SET {{N}}=1
@LABEL PRINT                                 
@GETDATE {{DATE}} -DDMMYY-
@GETTIME {{TIME}} -HHMM
@GETDAY {{DAY}} SUN MON TUE WED THU FRI SAT
@SET {{D}}="S:\\vendor_ericsson\\IRS\\Guan\\2G\\NB17042025\\POST-RXSTG-"
@@LOG FILE NAME
    """
    for i, cell in enumerate(cell_list, start=1):
        line_st = f'@IF {{N}} = {i}   THEN @SET {{S}} ="{cell}"+{{DATE}}+{{DAY}}+{{TIME}}+.log" \n'    
        section += line_st

    section += "@@BSC \n"

    for i, bsc in enumerate(bsc_new_list, start=1):
        line_bsc = f'@IF {{N}} = {i}   THEN @SET {{BSC}} ="{bsc}" \n'    
        section += line_bsc

    section += "@@ TG \n"

    for i, rxstg in enumerate(rxstg_new_list, start=1):
        line_tg = f'@IF {{N}} = {i}   THEN @SET {{TG}} =RXSTG-{rxstg}\n'
        section += line_tg

    section += "@@ CELL ID \n"

    for i, cell in enumerate(cell_list, start=1):
        line_cell = f'@IF {{N}} = {i}  THEN @SET {{CELL}} = {cell}" \n'    
        section += line_cell

    section += f"""
@T 1 
@LOG ON {{D}}{{S}} 
RXMOP:MO={{TG}}; 
@RITEM {{TRM}} {{_LINE8}} " " 0
RXCDP:MO={{TG}}; 
RXTCP:MO={{TG}}; 
@LABEL RLDEP
RLDEP:CELL={{CELL}};
RLCCP:CELL={{CELL}};
RLCPP:CELL={{CELL}};
RLBCP:CELL={{CELL}};
RLSLP:CELL={{CELL}};
RLIHP:CELL={{CELL}};
RLLCP:CELL={{CELL}};
RLIMP:CELL={{CELL}};
RLHPP:CELL={{CELL}};
RLPCP:CELL={{CELL}};
RLAPP:CELL={{CELL}};
RLSSP:CELL={{CELL}};
RLLOP:CELL={{CELL}};
RLCXP:CELL={{CELL}};
RLLDP:CELL={{CELL}};
RLLPP:CELL={{CELL}};
RLSBP:CELL={{CELL}};
RLSUP:CELL={{CELL}};
RLLHP:CELL={{CELL}};
RLACP:CELL={{CELL}};
RLGSP:CELL={{CELL}};
RLDHP:CELL={{CELL}};
RLDUP:CELL={{CELL}};
RLDGP:CELL={{CELL}};
RLCHP:CELL={{CELL}};
RLCFP:CELL={{CELL}};
RLBDP:CELL={{CELL}};
RLDTP:CELL={{CELL}};
RLUMP:CELL={{CELL}};
RLMFP:CELL={{CELL}};
RLLFP:CELL={{CELL}};
RLPDP:CELL={{CELL}};
RLGAP:CELL={{CELL}};
RLLUP:CELL={{CELL}};
RLDMP:CELL={{CELL}};
RLSRP:CELL={{CELL}};
RLCDP:CELL={{CELL}};
RLSMP:CELL={{CELL}};
RLCLP:CELL={{CELL}};
RLCSP:CELL={{CELL}};
RLPBP:CELL={{CELL}};
RLDEP:CELL={{CELL}}; 
RLCFP:CELL={{CELL}}; 
RLBDP:CELL={{CELL}}; 
RLCRP:CELL={{CELL}}; 
RLGSP:CELL={{CELL}}; 
RLGRP:CELL={{CELL}}; 
RLLOP:CELL={{CELL}}; 
RLCPP:CELL={{CELL}}; 
RLSLP:CELL={{CELL}}; 
RLCHP:CELL={{CELL}};  
RLCCP:CELL={{CELL}}; 
RLSTP:CELL={{CELL}}; 
RLSBP:CELL={{CELL}}; 
RLNRP:CELL={{CELL}},CELLR=ALL,NODATA;
RLNRP:CELL={{CELL}},CELLR=ALL,UTRAN;    
@LABEL RXMFP
RXMOP:MO={{TG}},SUBORD;
RXMFP:MO={{TG}},SUBORD;
RXMFP:MO={{TG}},SUBORD,FAULTY; 
RXMSP:MO={{TG}},SUBORD;
RXASP:MO={{TG}};
RXAPP:MO={{TG}};
RXTCP:MO={{TG}};
RXCDP:MO={{TG}}; 
CACLP;    
@LOG OFF 
@T 1 
@INC {{N}} 1 
@IF {{N}} <= {row_length} THEN GOTO PRINT
@LABEL STOP
    """
    script_lines.append(section)

    # Join all lines into one string with newlines
    script_output = "\n".join(script_lines)

    return script_output