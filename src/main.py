import pandas as pd
import os


sheet = pd.read_csv(
    os.path.abspath(
        os.path.join(__file__, "../..", "data/sheet.csv")
    )
)

sheet.sort_values(by="Average", ascending=False, inplace=True)

print("debug")