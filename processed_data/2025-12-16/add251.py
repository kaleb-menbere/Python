import pandas as pd

# --- Step 1: Read the CSV ---
df = pd.read_csv("KULU-Segment 1-300k.csv", dtype=str)  # ensure numbers are read as strings

# --- Step 2: Add '251' in front of numbers starting with '9' ---
added_count = 0

def add_prefix(num):
    global added_count
    if num.startswith('9'):
        added_count += 1
        return '251' + num
    return num

df['Contact'] = df['Contact'].apply(add_prefix)

# --- Step 3: Save to a new CSV ---
df.to_csv("KULU-Segment 1-300k Clean.csv", index=False)

# --- Step 4: Print report ---
print(f"Total numbers processed: {len(df)}")
print(f"Numbers updated with '251': {added_count}")
