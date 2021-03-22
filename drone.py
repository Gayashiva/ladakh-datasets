import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cmath, math

import logging
import coloredlogs


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
coloredlogs.install(
    fmt="%(levelname)s %(message)s",
    logger=logger,
)


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
    locations = ["guttannen"]
    for site in locations:
        logger.info(site)
        df1 = pd.read_csv(
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
        df1 = df1.iloc[::2]
        df1["When"] = pd.to_datetime(df1["When"], format="%b_%d_%y")
        logger.info(df1.When.head())
        df1 = df1.drop(columns=["FillVError", "CutVError", "TotalVError"])
        df1 = df1.set_index("When").sort_index()
        df1 = df1.astype(float)

        df2 = pd.read_csv(
            "drone_volumes/" + site + "_area.txt",
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
        df2["When"] = pd.to_datetime(df2["Name"], format="%b_%d_%y")
        df2 = df2.drop(columns=["Name"])
        df2 = df2[df2.columns.drop(list(df2.filter(regex="Error")))]
        df2 = df2[df2.columns.drop(list(df2.filter(regex="2D")))]
        df2 = df2.set_index("When").sort_index()
        df2 = df2.astype(float)
        cols2 = df2.columns
        cols = df1.columns
        df2[cols2[2:]] = df1[cols[1:]]
        df = df2
        df["Area"] = df1["Area"]
        df["dia"] = df2["3D Length"] / 3.14
        df = df.round(2)
        df.to_csv("outputs/" + site + "_drone.csv")
        # df2[cols2[1:]] = df2[cols2[1:]].apply(pd.to_numeric, errors="coerce")
        # logger.warning(df2.head())

        # df1["Height"] = 5
        # df["dia"] = 0
        # df = df.reset_index()
        # if site == "kullum":
        #     heights = [4, 11, 12, 12, 14]
        #     # areas = [173, 501, 619, 619, 586]
        #     areas = [197, 606, 707, 707, 641]
        #     for i in range(df.shape[0] - 1):
        #         df.loc[i, "Height"] = heights[i]
        #         df.loc[i, "Area"] = areas[i]
        # if site == "gangles":
        #     heights = [8, 13]
        #     areas = [194, 771]
        #     for i in range(len(heights)):
        #         df.loc[i, "Height"] = heights[i]
        #         df.loc[i, "Area"] = areas[i]
        # if site == "guttannen":
        #     heights = [0.1, 1, 2.4, 4, 2.7]
        #     for i in range(len(heights)):
        #         df.loc[i, "Height"] = heights[i]

        # for i in range(df.shape[0]):
        #     k = (df.Area[i] / 3.14) ** 2 * -1
        #     sol = quad_eqn(a=1, b=df.Height[i], c=k)
        #     df.loc[i, "dia"] = 2 * np.sqrt(sol)

        # df["V"] = 1 / 3 * 3.14 * df.dia ** 2 / 4 * df.Height
        # print(df.head())
