import pandas as pd

df = pd.read_csv("cleaned_file.csv", dtype=str)

prefixes = (
    "91120","91121","91122","91123","91124","91125",
    "91126","91127","91128","91129","91130",
    "91150","91151","91152","930"
)

result = df[df["Contact"].str.startswith(prefixes, na=False)]

print(result)
