import pandas as pd

df = pd.read_excel("nlsfb-ifcapps-extract.xlsx", sheet_name="Sheet 1")
df.to_json("nlsfb-ifcapps-extract.json", orient="records", indent=2, force_ascii=False)
