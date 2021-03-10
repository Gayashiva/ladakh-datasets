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


def add_data(site):

    df = pd.read_csv(
        "outputs/" + site + "_input.csv",
        sep=",",
        parse_dates=["When"],
    )
    df1 = pd.read_csv(
        "outputs/" + "SECMOL_input_field.csv",
        sep=",",
        parse_dates=["When"],
    )
    # start_date = df1.When[0]
    # # end_date = df1["When"].iloc[-1]
    # end_date=datetime(2021, 2, 22)
    # mask = df["When"] >= start_date & (df["When"] <= end_date)
    # df = df.loc[mask]
    # df = df.reset_index(drop=True)
    # mask = df1["When"] >= start_date #& (df1["When"] <= end_date)
    # df1 = df1.loc[mask]
    # df1 = df1.reset_index(drop=True)

    df = df.set_index("When")
    df1 = df1.set_index("When")
    cols = ["SW_direct", "SW_diffuse"]
    for col in cols:
        df.loc[:, col] = df1[col]

    df = df.reset_index()
    df = df[df.columns.drop(list(df.filter(regex="Unnamed")))]
    df = df.dropna()
    return df


def plot(df):

    filename = "outputs/" + site + "_input_field.pdf"
    pp = PdfPages(filename)
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(
        nrows=4, ncols=1, sharex="col", sharey="row", figsize=(16, 14)
    )

    x = df.When

    y1 = df.T_a
    ax1.plot(x, y1, "k-", linewidth=0.5)
    ax1.set_ylabel("Temperature [$\\degree C$]")
    ax1.grid()

    y2 = df.RH
    ax2.plot(x, y2, "k-", linewidth=0.5)
    ax2.set_ylabel("Humidity [$\\%$]")
    ax2.grid()

    y3 = df.v_a
    ax3.plot(x, y3, "k-", linewidth=0.5)
    ax3.set_ylabel("Wind [$m\\,s^{-1}$]")
    ax3.grid()

    y4 = df.p_a
    ax4.plot(x, y4, "k-", linewidth=0.5)
    ax4.set_ylabel("Pressure [$hPa$]")
    ax4.grid()

    # y5 = df.LW_in
    # ax5.plot(x, y5, "k-", linewidth=0.5)
    # ax5.set_ylabel("Radiation [$W\\,m^{-2}$]")
    # ax5.grid()

    # y6 = df.SW_global
    # ax6.plot(x, y6, "k-", linewidth=0.5)
    # ax6.set_ylabel("Radiation [$W\\,m^{-2}$]")
    # ax6.grid()

    ax1.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax1.xaxis.set_minor_locator(mdates.DayLocator())
    fig.autofmt_xdate()
    pp.savefig(bbox_inches="tight")
    pp.close()
    plt.clf()


if __name__ == "__main__":
    locations = ["HIAL", "Gangles", "SECMOL"]
    for site in locations:
        if site == "SECMOL":
            col_list = [
                "TIMESTAMP",
                "AirTC_Avg",
                "RH",
                "WS",
                "Incoming_SW_Avg",
                "Incoming_LW_Avg",
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
                    "Incoming_SW_Avg": "SW_global",
                    "Incoming_LW_Avg": "LW_in",
                },
                inplace=True,
            )
            for col in df_in:
                if col != "When":
                    df_in[col] = pd.to_numeric(df_in[col], errors="coerce")

            df_in1 = pd.read_csv(
                "data/" + site + "/SECMOL_Table60Min.dat",
                sep=",",
                skiprows=[0, 2, 3],
                parse_dates=["TIMESTAMP"],
            )
            df_in1.rename(
                columns={
                    "TIMESTAMP": "When",
                    "BP_mbar": "p_a",  # mbar same as hPa
                },
                inplace=True,
            )

            for col in df_in1:
                if col != "When":
                    df_in1[col] = pd.to_numeric(df_in1[col], errors="coerce")

            df_in = df_in.set_index("When")
            df_in1 = df_in1.set_index("When")

            df_in1 = df_in1.reindex(
                pd.date_range(df_in1.index[0], df_in1.index[-1], freq="15Min"),
                fill_value=np.NaN,
            )

            df_in = df_in.replace("NAN", np.NaN)
            df_in1 = df_in1.replace("NAN", np.NaN)
            df_in1 = df_in1.resample("15Min").interpolate("linear")
            df_in = df_in.resample("15Min").interpolate("linear")
            df_in.loc[:, "p_a"] = df_in1["p_a"]
            cols = ["T_a", "RH", "v_a", "p_a", "LW_in", "SW_global"]
            df_in["SW_diffuse"] = df_in.SW_global * 0.25
            df_in["SW_direct"] = df_in.SW_global * 0.75
            if df_in.isnull().values.any():
                print(site)
                print("Warning: Null values present")
                print(df_in[cols].isnull().sum())
            df_in = df_in.round(3)
            df_in = df_in.reset_index()
            df_in.rename(
                columns={
                    "index": "When",
                },
                inplace=True,
            )
            start_date = datetime(2020, 12, 14)
            mask = df_in["When"] >= start_date
            df_in = df_in.loc[mask]
            df_in = df_in.reset_index(drop=True)
            print(df_in.head())
            print(df_in.tail())
            df_in.to_csv("outputs/" + site + "_input_field.csv")
            # plot(df_in)

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

            # df_in = df_in.reindex(
            #     pd.date_range(df_in.index[0], df_in.index[-1], freq="15Min"),
            #     fill_value=np.NaN,
            # )

            df_in1 = pd.read_csv(
                "data/" + site + "/Gangles_Table60Min.dat",
                sep=",",
                skiprows=[0, 2, 3],
                parse_dates=["TIMESTAMP"],
            )
            df_in1.rename(
                columns={
                    "TIMESTAMP": "When",
                    "BP_mbar": "p_a",  # mbar same as hPa
                },
                inplace=True,
            )

            for col in df_in1:
                if col != "When":
                    df_in1[col] = pd.to_numeric(df_in1[col], errors="coerce")

            df_in = df_in.set_index("When")
            df_in1 = df_in1.set_index("When")

            df_in1 = df_in1.reindex(
                pd.date_range(df_in1.index[0], df_in1.index[-1], freq="15Min"),
                fill_value=np.NaN,
            )

            df_in = df_in.replace("NAN", np.NaN)
            df_in1 = df_in1.replace("NAN", np.NaN)
            df_in1 = df_in1.resample("15Min").interpolate("linear")
            # df_in = df_in.resample("15Min").interpolate("linear")
            df_in.loc[:, "p_a"] = df_in1["p_a"]

            df_in = df_in.replace("NAN", np.NaN)
            if df_in.isnull().values.any():
                print(site)
                print("Warning: Null values present")
                print(df_in[cols].isnull().sum())
            df_in = df_in.round(3)
            df_in = df_in.reset_index()
            df_in.rename(
                columns={
                    "index": "When",
                },
                inplace=True,
            )
            start_date = datetime(2020, 12, 14)
            mask = df_in["When"] >= start_date
            df_in = df_in.loc[mask]
            df_in = df_in.reset_index(drop=True)
            print(df_in.head())
            print(df_in.tail())
            df_in.to_csv("outputs/" + site + "_input.csv")
            df = add_data(site)
            df.to_csv("outputs/" + site + "_input_field.csv")
            # plot(df_in)

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
            for col in df_in:
                df_in[col] = pd.to_numeric(df_in[col], errors="coerce")
                # df_in[col].interpolate(method="linear")
            df_in = df_in.resample("15Min").interpolate("linear")
            if df_in.isnull().values.any():
                print(site)
                print("Warning: Null values present")
                print(df_in[cols].isnull().sum())

            df_in = df_in.round(3)
            df_in = df_in.reset_index()
            df_in.rename(
                columns={
                    "index": "When",
                },
                inplace=True,
            )
            df_in["SW_diffuse"] = df_in.SW_global * 0.25
            df_in["SW_direct"] = df_in.SW_global * 0.75

            print(df_in.head())
            print(df_in.tail())
            start_date = datetime(2020, 12, 14)
            mask = df_in["When"] >= start_date
            df_in = df_in.loc[mask]
            df_in = df_in.reset_index(drop=True)
            df_in.to_csv("outputs/" + site + "_input_field.csv")
