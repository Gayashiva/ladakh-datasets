import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import math
import time
from tqdm import tqdm
import os

if __name__ == "__main__":
    name = "HIAL"
    col_list = [
        "TIMESTAMP",
        "T107_probe_Avg",
        "RH_probe_Avg",
        "amb_press_Avg",
        "WS",
        "SnowHeight",
        "SW_IN",
        "LW_IN",
    ]
    cols = ["T_a", "RH", "v_a", "p_a", "SW_global", "LW_in"]

    df_in = pd.read_csv(
        "data/" + name + "/HIAL_3Dec_22Feb.dat",
        sep=",",
        skiprows=[0, 2, 3],
        parse_dates=["TIMESTAMP"],
    )
    df_in = df_in[col_list]
    end = df_in.loc[df_in["TIMESTAMP"] == datetime(2020, 12, 28, 13)].index.values
    df_in = df_in.iloc[: int(end + 1)]
    df_in.rename(
        columns={
            "TIMESTAMP": "When",
            "T107_probe_Avg": "T_a",
            "RH_probe_Avg": "RH",
            "amb_press_Avg": "p_a",
            "WS": "v_a",
            "SW_IN": "SW_global",
            "LW_IN": "LW_in",
        },
        inplace=True,
    )
    df_in = df_in.set_index("When")

    end = "2021-02-22 12:30:00"
    df_in = df_in.reindex(
        pd.date_range(df_in.index[0], end, freq="30Min"), fill_value=np.NaN
    )

    files = [
        "HIAL_19Dec_26Dec",
        "HIAL_2Jan_9Jan",
        "HIAL_9Jan_14Jan",
        "HIAL_16Jan_17Jan",
        "HIAL_19Jan_22Feb",
    ]
    for file in files:

        df_in1 = pd.read_csv(
            "data/" + name + "/" + file + ".dat",
            sep=",",
            skiprows=[0, 2, 3],
            parse_dates=["TIMESTAMP"],
        )
        df_in1 = df_in1[col_list]
        df_in1.rename(
            columns={
                "TIMESTAMP": "When",
                "T107_probe_Avg": "T_a",
                "RH_probe_Avg": "RH",
                "amb_press_Avg": "p_a",
                "WS": "v_a",
                "SW_IN": "SW_global",
                "LW_IN": "LW_in",
            },
            inplace=True,
        )
        df_in1 = df_in1.set_index("When")

        # Fill
        df_in.loc[df_in["T_a"].isnull(), cols] = df_in1[cols]

    print(df_in.loc[df_in.T_a.isnull()])

    df_in = df_in.replace("NAN", np.NaN)
    df_out = df_in
    if df_out.isnull().values.any():
        print("Warning: Null values present")
        print(df_out[cols].isnull().sum())
    print(df_out.head())
    print(df_out.tail())

    df_in.to_csv("outputs/" + name + "_input_field.csv")
