import pandas as pd
import random

# Number of random phone numbers
num_random = 950
num_duplicates = 30
num_vip = 20

# 1️⃣ Generate random Ethiopian numbers (2519XXXXXXX)
random_numbers = ["2519" + "".join([str(random.randint(0, 9)) for _ in range(7)]) for _ in range(num_random)]

# 2️⃣ Create some duplicates (pick randomly from random_numbers)
duplicates = random.choices(random_numbers, k=num_duplicates)

# 3️⃣ Add VIP numbers
vip_prefixes = [
    "91120", "91121", "91122", "91123", "91124", "91125",
    "91126", "91127", "91128", "91129", "91130",
    "9150", "9151", "9152",
    "911", "930", "912", "913"
]

vip_numbers = []
for prefix in vip_prefixes:
    # Add one number for each prefix with random ending
    if prefix.startswith("9112") or prefix.startswith("915") or len(prefix) == 3:
        length_needed = 9 - len(prefix)  # Ethiopian numbers typically 9 digits after 251?
        number = prefix + "".join([str(random.randint(0,9)) for _ in range(length_needed)])
        vip_numbers.append(number)

# Combine all numbers
all_numbers = random_numbers + duplicates + vip_numbers

# Shuffle for randomness
random.shuffle(all_numbers)

# Create DataFrame
df_sample = pd.DataFrame({"Contact": all_numbers})

# Save CSV
df_sample.to_csv("sample_with_duplicates_vip.csv", index=False)

print("Sample CSV created: sample_with_duplicates_vip.csv")
print(f"Total numbers: {len(df_sample)} (including {num_duplicates} duplicates and {len(vip_numbers)} VIP numbers)")
