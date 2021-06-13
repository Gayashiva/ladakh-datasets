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
import logging
import coloredlogs


def add_data(site):

    df = pd.read_csv(
        "outputs/" + site + "_input.csv",
        sep=",",
        parse_dates=["When"],
    )
    df1 = pd.read_csv(
        "outputs/" + "HIAL_input_field.csv",
        sep=",",
        parse_dates=["When"],
    )

    df = df.set_index("When")
    df1 = df1.set_index("When")
    cols = ["SW_global"]
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
    logger = logging.getLogger(__name__)
    coloredlogs.install(
        fmt="%(funcName)s %(levelname)s %(message)s",
        level=logging.INFO,
        logger=logger,
    )
    # locations = ["HIAL", "Gangles", "SECMOL"]
    # locations = ["Gangles", "SECMOL"]
    locations = ["Gangles", "HIAL"]
    for site in locations:
        if site == "HIAL":
            col_list = [
                "TIMESTAMP",
                "AirTC_Avg",
                "RH",
                "WS",
                "Incoming_SW_Avg",
                "Incoming_LW_Avg",
            ]

            df_in = pd.read_csv(
                "data/" + site + "/CR1000_Table15min.dat",
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

            # Extend dataframe
            dfx = pd.read_csv(
                "data/" + site + "/CR1000_Table15min.dat",
                sep=",",
                skiprows=[0, 2, 3],
                parse_dates=["TIMESTAMP"],
            )
            dfx = dfx[col_list]
            dfx.rename(
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
            end_date = df_in["When"].iloc[-1]
            mask = dfx["When"] > end_date
            dfx = dfx.loc[mask]
            dfx = dfx.reset_index(drop=True)
            dfx = dfx.set_index("When")
            df_in = df_in.set_index("When")
            df_in = df_in.append(dfx)
            df_in = df_in.reset_index()

            for col in df_in:
                if col != "When":
                    df_in[col] = pd.to_numeric(df_in[col], errors="coerce")
            df_in = df_in.replace("NAN", np.NaN)

            df_in1 = pd.read_csv(
                "data/" + site + "/CR1000_Table60Min.dat",
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
            # Extend dataframe
            dfx = pd.read_csv(
                "data/" + site + "/CR1000_Table60Min.dat",
                sep=",",
                skiprows=[0, 2, 3],
                parse_dates=["TIMESTAMP"],
            )
            col_list = [
                "TIMESTAMP",
                "BP_mbar",
            ]
            dfx = dfx[col_list]
            dfx.rename(
                columns={
                    "TIMESTAMP": "When",
                    "BP_mbar": "p_a",  # mbar same as hPa
                },
                inplace=True,
            )
            end_date = df_in1["When"].iloc[-1]
            mask = dfx["When"] > end_date
            dfx = dfx.loc[mask]
            dfx = dfx.reset_index(drop=True)
            dfx = dfx.set_index("When")
            df_in1 = df_in1.set_index("When")
            df_in1 = df_in1.append(dfx)
            df_in1 = df_in1.reset_index()

            for col in df_in1:
                if col != "When":
                    df_in1[col] = pd.to_numeric(df_in1[col], errors="coerce")
            df_in1 = df_in1.replace("NAN", np.NaN)

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
            # df_in["SW_diffuse"] = 0
            # df_in["SW_direct"] = df_in.SW_global
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
            if df_in.isna().values.any():
                logger.error(df_in.isna().sum())
                for column in df_in:
                    if df_in[column].isna().sum() > 0 and column != "When":
                        logger.warning("Warning: Null values filled in %s" % column)
                        df_in.loc[:, column] = df[column].interpolate()
            print(df_in.head())
            print(df_in.tail())
            df_in.to_csv("outputs/" + site + "_input_field.csv")
            plot(df_in)

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

            mask = df["SW_global"] < 0
            mask_index = df[mask].index
            df.loc[mask_index, 'SW_global'] = 0
            diffuse_fraction = 0
            df["SW_diffuse"] = diffuse_fraction * df.SW_global
            df["SW_direct"] = (1-diffuse_fraction)* df.SW_global
            df["Prec"] = 0
            df["missing_type"] ='-'
            df["cld"] = 0
            site = "gangles21"
            df.to_csv(
                "/home/suryab/work/air_model/data/"
                + site
                + "/interim/"
                + site
                + "_input_model.csv"
            )
            plot(df)
