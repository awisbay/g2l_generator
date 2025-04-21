import pandas as pd

# Load Excel file
excel_file = "MD-QC-BSC-Template-20220622_102727.xlsx"  # Adjust path as needed
df = pd.read_excel(excel_file)

# Ensure required columns
df = df[['CELL', 'BSC_LEGACY', 'RSITE', 'RXOTG_LEGACY']]
row_length = len(df)

# Function to generate script by grouping RSITE
def generate_script_by_rsite(data):
    
    lines = []
    n_blocks = []

    lines.append(f"""@SET {{N}}=1
@LABEL PRINT                                 
@GETDATE {{DATE}} -DDMMYY-
@GETTIME {{TIME}} -HHMM
@GETDAY {{DAY}} SUN MON TUE WED THU FRI SAT
@SET {{D}}="S:\\vendor_ericsson\\IRS\\Guan\\WinFiol\\Log\\"
@@LOG FILE NAME\n"""
    )

    # Group by RSITE
    for n, (rsite, group) in enumerate(data.groupby("RSITE"), start=1):
        bsc = group.iloc[0]['BSC_LEGACY']
        tg = group.iloc[0]['RXOTG_LEGACY']
        cells = group['CELL'].tolist()

        n_blocks.append({
            "N": n,
            "RSITE": rsite,
            "BSC": bsc,
            "TG": tg,
            "CELL": cells
        })

    # Filename lines
    lines.append("".join([
        f'@IF {{N}} = {block["N"]}   THEN @SET {{S}} ="{block["RSITE"]}"+{{DATE}}+{{DAY}}+{{TIME}}+".log"\n'
        for block in n_blocks
    ]))

    # BSC section
    lines.append('@@BSC\n')
    lines.append("".join([
        f'@IF {{N}} = {block["N"]}   THEN @SET {{BSC}} ="{block["BSC"]}"\n'
        for block in n_blocks
    ]))

    # TG section
    lines.append('@@ TG\n')
    lines.append("".join([
        f'@IF {{N}} = {block["N"]}   THEN @SET {{TG}} ={block["TG"]}\n'
        for block in n_blocks
    ]))

    # CELL grouped line
    lines.append('@@ CELL ALL\n')
    lines.append("".join([
        f'@IF {{N}} = {block["N"]}   THEN @SET {{CELL}} ={"& ".join(block["CELL"])}\n'
        for block in n_blocks
    ]))

    # CELL1, CELL2, CELL3, etc.
    
    max_cells = max(len(block["CELL"]) for block in n_blocks)
    for i in range(max_cells):
        lines.append(f'@@ CELL ID {i+1:02d}\n')
        lines.append("".join([
            f'@IF {{N}} = {block["N"]}   THEN @SET {{CELL{i+1}}} = {block["CELL"][i]}\n'
            if i < len(block["CELL"]) else ''
            for block in n_blocks
        ]))
    lines.append(f"""@T 2
exit;
@T 2
eaw {{BSC}}
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
RLNRP:cell={{CELL}},cellr=all; 
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
@IF {{N}} <= {len(n_blocks)} THEN GOTO PRINT
@LABEL STOP""")

    final_script = ''.join(lines)

    return final_script
