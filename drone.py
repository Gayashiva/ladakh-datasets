import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cmath, math


def quad_eqn(a, b, c):
    # calculate the discriminant
    d = (b ** 2) - (4 * a * c)

    # find two solutions
    sol1 = (-b - math.sqrt(d)) / (2 * a)
    sol2 = (-b + math.sqrt(d)) / (2 * a)

    # print("The solution are {0} and {1}".format(sol1, sol2))

    if sol1 > 0:
        return sol1
    else:
        return sol2


if __name__ == "__main__":
    # locations = ["gangles", "guttannen", "kullum"]
    locations = ["gangles"]
    for site in locations:
        print(site)
        df = pd.read_csv(
            "drone_volumes/" + site + "_volumes.txt",
            sep="\t",
            skiprows=[0],
            names=[
                "When",
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
        df["When"] = pd.to_datetime(df["When"], format="%m_%d_%Y_%H")
        df = df.drop(columns=["FillVError", "CutVError", "TotalVError"])
        df = df.set_index("When").sort_index()
        df = df.astype(float)
        df["Height"] = 5
        df["dia"] = 0
        # df["Slope"] = np.sqrt((3 * df["Area"] / 3.14) - 1)
        # df["Dia"] = 2 * df.Height / df.Slope
        df = df.reset_index()
        if site == "kullum":
            heights = [4, 11, 12, 12, 14]
            # areas = [173, 501, 619, 619, 586]
            areas = [197, 606, 707, 707, 641]
            for i in range(df.shape[0] - 1):
                df.loc[i, "Height"] = heights[i]
                df.loc[i, "Area"] = areas[i]
        if site == "gangles":
            heights = [8, 13]
            areas = [194, 771]
            for i in range(len(heights)):
                df.loc[i, "Height"] = heights[i]
                df.loc[i, "Area"] = areas[i]
        if site == "guttannen":
            heights = [0.1, 1, 2.4, 4, 2.7]
            for i in range(len(heights)):
                df.loc[i, "Height"] = heights[i]

        for i in range(df.shape[0]):
            k = (df.Area[i] / 3.14) ** 2 * -1
            sol = quad_eqn(a=1, b=df.Height[i], c=k)
            df.loc[i, "dia"] = 2 * np.sqrt(sol)

        df["V"] = 1 / 3 * 3.14 * df.dia ** 2 / 4 * df.Height
        print(df.head())
        df.to_csv("outputs/" + site + "_drone.csv")
