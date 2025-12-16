import pandas as pd
import random

# Generate 1000 random phone numbers starting with Ethiopia code 2519XXXXXXX
phone_numbers = ["2519" + "".join([str(random.randint(0,9)) for _ in range(7)]) for _ in range(1000)]

df_sample = pd.DataFrame({"Contact": phone_numbers})
df_sample.to_csv("sample.csv", index=False)

print("Sample CSV with 1000 phone numbers created: sample.csv")
