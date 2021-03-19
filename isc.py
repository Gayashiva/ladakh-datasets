import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

if __name__ == "__main__":
    df = pd.read_csv(
        "drone_volumes/" + "isc_volumes.txt",
        sep="\t",
        skiprows=[0],
        names=[
            "Name",
            "Area",
            "FillV",
            "FillVError",
            "CutV",
            "CutVError",
            "TotalV",
            "TotalVError",
        ],
    )
    df = df.iloc[::2]
    cols = df.columns
    df[cols[1:]] = df[cols[1:]].apply(pd.to_numeric, errors="coerce")
    df = df.sort_values(by=["TotalV"], ascending=False, ignore_index=True)
    df2 = pd.read_csv(
        "drone_volumes/" + "area_circum.csv",
        sep="\t",
        index_col=False,
        skiprows=[0],
        names=[
            "Name",
            "2D Length",
            "2D Length Error",
            "3D Length",
            "3D Length Error",
            "2D Area",
            "2D Area Error",
            "3D Area",
            "3D Area Error",
            "FillV",
            "FillVError",
            "CutV",
            "CutVError",
            "TotalV",
            "TotalVError",
        ],
    )
    df2 = df2.iloc[::2]
    cols2 = df2.columns
    df2[cols2[1:]] = df2[cols2[1:]].apply(pd.to_numeric, errors="coerce")
    df2 = df2.set_index("Name")
    df = df.set_index("Name")
    df2[cols2[9:]] = df[cols[2:]]
    df2["Area"] = df["Area"]
    df2 = df2.drop(columns=["2D Length Error", "3D Length Error", "2D Area Error"])
    df2 = df2.reset_index()
    df = df2.sort_values(by=["TotalV"], ascending=False, ignore_index=True)
    df["TotalV"] = df["TotalV"].round(2)
    # df2 = df[["Name", "TotalV"]]
    # df2.to_csv("outputs/" + "isc_results.csv")

    # cols = [c for c in df.columns if c.lower() != "error"]
    # df = df[cols]
    df = df[df.columns.drop(list(df.filter(regex="Error")))]
    df["NewV"] = df["3D Area"] * 1.5 + df["TotalV"]
    df["NewV"] = df["NewV"].round(2)
    print(df.head(10))
    df2 = df[["Name", "TotalV", "NewV"]]
    df2.to_csv("outputs/" + "isc_results.csv")
    print(df2.head(10))
