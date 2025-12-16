import pandas as pd

# Load Excel file
df = pd.read_excel("300k.xlsx", dtype=str)  # dtype=str preserves numbers exactly

# Save as CSV without changing numbers
df.to_csv("300k.csv", index=False)
