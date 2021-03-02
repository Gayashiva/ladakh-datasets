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
    locations = ["HIAL", "Gangles", "SECMOL"]
    for site in locations:
        if site == "SECMOL":
            col_list = [
                "TIMESTAMP",
                "AirTC_Avg",
                "RH",
                "WS",
            ]
            cols = ["T_a", "RH", "v_a"]

            df_in = pd.read_csv(
                "data/" + site + "/SECMOL_Table15min.dat",
                sep=",",
                skiprows=[0, 2, 3],
                parse_dates=["TIMESTAMP"],
            )
            df_in = df_in[col_list]

            df_in.rename(
                columns={
                    "TIMESTAMP": "When",
                    "AirTC_Avg": "T_a",
                    "RH_probe_Avg": "RH",
                    "WS": "v_a",
                },
                inplace=True,
            )

            df_in = df_in.set_index("When")

            df_in = df_in.reindex(
                pd.date_range(df_in.index[0], df_in.index[-1], freq="15Min"),
                fill_value=np.NaN,
            )

            df_in = df_in.replace("NAN", np.NaN)
            if df_in.isnull().values.any():
                print("Warning: Null values present")
                print(df_in[cols].isnull().sum())
            print(df_in.head())
            print(df_in.tail())
            df_in.to_csv("outputs/" + site + "_input_field.csv")
        if site == "Gangles":
            col_list = [
                "TIMESTAMP",
                "AirTC_Avg",
                "RH",
                "WS",
            ]
            cols = ["T_a", "RH", "v_a"]

            df_in = pd.read_csv(
                "data/" + site + "/Gangles_Table15Min.dat",
                sep=",",
                skiprows=[0, 2, 3, 4],
                parse_dates=["TIMESTAMP"],
            )
            df_in = df_in[col_list]

            df_in.rename(
                columns={
                    "TIMESTAMP": "When",
                    "AirTC_Avg": "T_a",
                    "RH_probe_Avg": "RH",
                    "WS": "v_a",
                },
                inplace=True,
            )

            df_in = df_in.set_index("When")

            df_in = df_in.reindex(
                pd.date_range(df_in.index[0], df_in.index[-1], freq="15Min"),
                fill_value=np.NaN,
            )

            df_in = df_in.replace("NAN", np.NaN)
            if df_in.isnull().values.any():
                print("Warning: Null values present")
                print(df_in[cols].isnull().sum())
            print(df_in.head())
            print(df_in.tail())
            df_in.to_csv("outputs/" + site + "_input_field.csv")

        if site == "HIAL":
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
                "data/" + site + "/HIAL_3Dec_22Feb.dat",
                sep=",",
                skiprows=[0, 2, 3],
                parse_dates=["TIMESTAMP"],
            )
            df_in = df_in[col_list]
            end = df_in.loc[
                df_in["TIMESTAMP"] == datetime(2020, 12, 28, 13)
            ].index.values
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
                    "data/" + site + "/" + file + ".dat",
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

            df_in = df_in.replace("NAN", np.NaN)
            if df_in.isnull().values.any():
                print("Warning: Null values present")
                print(df_in[cols].isnull().sum())
            print(df_in.head())
            print(df_in.tail())

            df_in.to_csv("outputs/" + site + "_input_field.csv")
