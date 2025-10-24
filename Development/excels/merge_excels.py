import pandas as pd
import glob
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

RING = 1

file_list = glob.glob(f"../results/Anomalies_PXRing_{RING}_202*.xlsx")
all_data = []

for file in file_list:
    df = pd.read_excel(file)
    all_data.append(df)

merged_df = pd.concat(all_data, ignore_index=True)
output_file = f"Merged_Anomalies_PXRing_{RING}.xlsx"

# Highlight rows where "Type" = "Multi-Disk"
def highlight_rows(row):
    if row["Type"] == "Multi-Disk":
        return ['background-color: #ADD8E6'] * len(row)
    return [''] * len(row)

# Apply the highlighting function
styled_df = merged_df.style.apply(highlight_rows, axis=1)
styled_df.to_excel(output_file, index=False, engine='openpyxl')

print(f"Merging complete. Saved as {output_file}")
