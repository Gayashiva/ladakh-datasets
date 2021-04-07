import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import math
import time
import os

if __name__ == "__main__":
    df = pd.read_csv(
        "data/flowmeter/" + "9feb_23mar.csv",
        # "data/flowmeter/" + "2feb_9feb.csv",
        # "data/flowmeter/" + "18thdec_9thfeb.csv",
        # "data/flowmeter/" + "all_18_12.csv",
        sep=";",
        # skiprows=[0, 2, 3],
        parse_dates=["Time"],
    )
    df["Min volume flow rate, m³/h"] = df["Min volume flow rate, m³/h"].str.replace(
        ",", "."
    )
    df["Max volume flow rate, m³/h"] = df["Min volume flow rate, m³/h"].str.replace(
        ",", "."
    )
    df["Min volume flow rate, m³/h"] = pd.to_numeric(
        df["Min volume flow rate, m³/h"], downcast="float"
    )
    df["Max volume flow rate, m³/h"] = pd.to_numeric(
        df["Min volume flow rate, m³/h"], downcast="float"
    )
    df["Discharge"] = (
        (df["Min volume flow rate, m³/h"] + df["Max volume flow rate, m³/h"]) / 2
    )
    col_list = [
        "Time",
        "Site",
        "Discharge",
    ]
    df = df[col_list]
    df.Discharge *= 1000 / 60
    df = df[df.Discharge != 0]
    grouped = df.groupby("Site")
    # print(grouped.get_group("Phaterak"))
    print(df.head(10))
