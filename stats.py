import math
import os
import pandas as pd
import numpy as np
import sys
from datetime import datetime

start_time = datetime.now()
# print(start_time.strftime("%c"))

index = 0
g = 9.81
OUTPUT_PATH = os.path.join("OUTPUT_DIR", "Results_Consolidated_v4.csv")
data = None
N = None

if not os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, mode="a") as f:
        row = [
            start_time.strftime("%c"),
            "average_velocity_U",
            "average_velocity_V",
            "average_velocity_W",
            "U_variance_Prime",
            "V_variance_Prime",
            "W_variance_Prime",
            "U_stdev_Prime",
            "V_stdev_Prime",
            "W_stdev_Prime",
            "Skewness_U_Prime",
            "Skewness_V_Prime",
            "Skewness_W_Prime",
            "Kurtosis_U_Prime",
            "Kurtosis_V_Prime",
            "Kurtosis_W_Prime",
            "Reynolds_stress_u'v'",
            "Reynolds_stress_u'w'",
            "Reynolds_stress_v'w'",
            "Anisotropy",
            "M30",
            "M03",
            "M12",
            "M21",
            "fku_2d",
            "Fku_2d",
            "fkw_2d",
            "Fkw_2d",
            "fku_3d",
            "Fku_3d",
            "fkw_3d",
            "Fkw_3d",
            "TKE_3d",
            "Q1_K_Value",
            "Q2_K_Value",
            "Q3_K_Value",
            "Q4_K_Value",
            "e",
            "ED",
            "Octant_plus_1",
            "Octant_minus_1",
            "Octant_plus_2",
            "Octant_minus_2",
            "Octant_plus_3",
            "Octant_minus_3",
            "Octant_plus_4",
            "Octant_minus_4",
            "Total_Octant_sample",
            "Probability_Octant_plus_1",
            "Probability_Octant_minus_1",
            "Probability_Octant_plus_2",
            "Probability_Octant_minus_2",
            "Probability_Octant_plus_3",
            "Probability_Octant_minus_3",
            "Probability_Octant_plus_4",
            "Probability_Octant_minus_4",
            "Min_Octant_Count",
            "Min_Octant_Count_id",
            "Max_Octant_Count",
            "Max_Octant_Count_id",
            "K",
            "TI",
        ]
        f.write(",".join(str(i) for i in row))
        f.write("\n")


def useful_values_u():
    data["Var_u'"] = data["std_u'"] = data["Skewness_u'"] = data["Kurtosis_u'"] = ""

    data["u'u'"] = round(data["u'"] ** 2, 8)
    data.at[0, "Var_u'"] = round(data["u'u'"].mean(), 8)  # variance
    u_std = round(data["u'"].std(), 8)
    data.at[0, "std_u'"] = u_std  # standard deviation
    data.at[0, "Skewness_u'"] = round(data["u'"].skew(), 8)  # skewness
    data.at[0, "Kurtosis_u'"] = round(data["u'"].kurt(), 8)  # kurtosis
    data["u^"] = round(data["u'"] / u_std, 8)


def useful_values_v():
    data["Var_v'"] = data["std_v'"] = data["Skewness_v'"] = data["Kurtosis_v'"] = ""

    data["v'v'"] = round(data["v'"] ** 2, 8)
    data.at[0, "Var_v'"] = round(data["v'v'"].mean(), 8)  # variance
    u_std = round(data["v'"].std(), 8)
    data.at[0, "std_v'"] = u_std  # standard deviation
    data.at[0, "Skewness_v'"] = round(data["v'"].skew(), 8)  # skewness
    data.at[0, "Kurtosis_v'"] = round(data["v'"].kurt(), 8)  # kurtosis
    data["v^"] = round(data["v'"] / u_std, 8)


def useful_values_w():
    data["Var_w'"] = data["std_w'"] = data["Skewness_w'"] = data["Kurtosis_w'"] = ""

    data["w'w'"] = round(data["w'"] ** 2, 8)
    data.at[0, "Var_w'"] = round(data["w'w'"].mean(), 8)  # variance
    w_std = round(data["w'"].std(), 8)
    data.at[0, "std_w'"] = w_std  # standard deviation
    data.at[0, "Skewness_w'"] = round(data["w'"].skew(), 8)  # skewness
    data.at[0, "Kurtosis_w'"] = round(data["w'"].kurt(), 8)  # kurtosis
    data["w^"] = round(data["w'"] / w_std, 8)


def useful_values():
    data["U_mean"] = data["V_mean"] = data["W_mean"] = ""
    U_mean = round(data["FILTERED_U"].mean(), 8)
    V_mean = round(data["FILTERED_V"].mean(), 8)
    W_mean = round(data["FILTERED_W"].mean(), 8)

    data.at[index, "U_mean"] = U_mean
    data.at[index, "V_mean"] = V_mean
    data.at[index, "W_mean"] = W_mean

    data["u'"] = round(data["FILTERED_U"] - U_mean, 8)
    data["v'"] = round(data["FILTERED_V"] - V_mean, 8)
    data["w'"] = round(data["FILTERED_W"] - W_mean, 8)
    N = data["FILTERED_U"].count()

    useful_values_u()
    useful_values_v()
    useful_values_w()

    data["Reynolds_stress_u'v'"] = data["Reynolds_stress_u'w'"] = data[
        "Reynolds_stress_v'w'"
    ] = ""

    data["u'v'"] = data["u'"] * data["v'"]
    data.at[0, "Reynolds_stress_u'v'"] = round(data["u'v'"].mean(), 8)

    data["u'w'"] = data["u'"] * data["w'"]
    data.at[0, "Reynolds_stress_u'w'"] = round(data["u'w'"].mean(), 8)

    data["v'w'"] = data["v'"] * data["w'"]
    data.at[0, "Reynolds_stress_v'w'"] = round(data["v'w'"].mean(), 8)

    data.at[0, "anisotropy"] = round(data.at[0, "std_w'"] / data.at[0, "std_u'"], 8)
    data["M30"] = data["M03"] = data["M12"] = data["M21"] = ""

    data["u^u^w^"] = round((data["u^"] ** 2) * (data["w^"]), 8)
    data["u^w^w^"] = round((data["w^"] ** 2) * (data["u^"]), 8)
    data["u^u^u^"] = round(data["u^"] ** 3, 8)
    data["w^w^w^"] = round(data["w^"] ** 3, 8)

    data.at[0, "M21"] = round(data["u^u^w^"].mean(), 8)
    data.at[0, "M12"] = round(data["u^w^w^"].mean(), 8)
    data.at[0, "M30"] = round(data["u^u^u^"].mean(), 8)
    data.at[0, "M03"] = round(data["w^w^w^"].mean(), 8)

    K = (
        round(data["u'u'"].mean(), 8)
        + round(data["v'v'"].mean(), 8)
        + round(data["w'w'"].mean(), 8)
    ) / 2
    TI = math.sqrt(
        (
            round(data["u'u'"].mean(), 8)
            + round(data["v'v'"].mean(), 8)
            + round(data["w'w'"].mean(), 8)
        )
        / 3
    )

    data.at[0, "K"] = K
    print("K =", K)

    TI = round(TI, 8)
    data.at[0, "TI"] = TI
    print("TI =", TI)


def fk():
    data["fku_2d"] = data["Fku_2d"] = data["fkw_2d"] = data["Fkw_2d"] = ""
    data["u'u'u'"] = round(data["u'"] ** 3, 8)
    data["u'u'u' mean"] = ""
    data.at[0, "u'u'u' mean"] = round(data["u'u'u'"].mean(), 8)

    data["u'w'w'"] = round((data["w'"] ** 2) * (data["u'"]), 8)
    data["u'w'w' mean"] = ""
    data.at[0, "u'w'w' mean"] = round(data["u'w'w'"].mean(), 8)

    data["w'w'w'"] = round(data["w'"] ** 3, 8)
    data["w'w'w' mean"] = ""
    data.at[0, "w'w'w' mean"] = round(data["w'w'w'"].mean(), 8)

    data["w'u'u'"] = round((data["u'"] ** 2) * (data["w'"]), 8)
    data["w'u'u' mean"] = ""
    data.at[0, "w'u'u' mean"] = round(data["w'u'u'"].mean(), 8)

    data["u'v'v'"] = round((data["v'"] ** 2) * (data["u'"]), 8)
    data["u'v'v' mean"] = ""
    data.at[0, "u'v'v' mean"] = round(data["u'v'v'"].mean(), 8)

    data["w'v'v'"] = round((data["v'"] ** 2) * (data["w'"]), 8)
    data["w'v'v' mean"] = ""
    data.at[0, "w'v'v' mean"] = round(data["w'v'v'"].mean(), 8)

    constant_fk2d = 0.75
    multiplying_factor_3d = 0.5
    Shear_velocity = 2.6**3

    data.at[index, "fku_2d"] = round(
        (data.at[0, "u'u'u' mean"] + data.at[0, "u'w'w' mean"]) * constant_fk2d, 8
    )
    data.at[index, "Fku_2d"] = round(data.at[index, "fku_2d"] / Shear_velocity, 8)

    data.at[index, "fkw_2d"] = round(
        (data.at[0, "w'w'w' mean"] + data.at[0, "w'u'u' mean"]) * constant_fk2d, 8
    )
    data.at[index, "Fkw_2d"] = round(data.at[index, "fkw_2d"] / Shear_velocity, 8)

    data["fku_3d"] = data["Fku_3d"] = data["fkw_3d"] = data["Fkw_3d"] = data[
        "TKE_3d"
    ] = ""

    data.at[index, "fku_3d"] = round(
        (
            data.at[0, "u'u'u' mean"]
            + data.at[0, "u'w'w' mean"]
            + data.at[0, "u'v'v' mean"]
        )
        * multiplying_factor_3d,
        8,
    )
    data.at[index, "Fku_3d"] = round(data.at[index, "fku_2d"] / Shear_velocity, 8)

    data.at[index, "fkw_3d"] = round(
        (
            data.at[0, "w'w'w' mean"]
            + data.at[0, "w'u'u' mean"]
            + data.at[0, "w'v'v' mean"]
        )
        * multiplying_factor_3d,
        8,
    )
    data.at[index, "Fkw_3d"] = round(data.at[index, "fkw_3d"] / Shear_velocity, 8)

    data.at[index, "TKE_3D"] = round(
        (data.at[0, "Var_v'"] * data.at[0, "Var_u'"] * data.at[0, "Var_w'"])
        * multiplying_factor_3d,
        8,
    )


def Q_K_Value():
    data["Q1_K_Value"] = data["Q2_K_Value"] = data["Q3_K_Value"] = data[
        "Q4_K_Value"
    ] = ""
    u_std = round(data["u'"].std(), 8)
    w_std = round(data["w'"].std(), 8)
    value = u_std * w_std
    X = 10000
    k_first = k_second = k_third = k_fourth = 0
    first = [0] * X
    second = [0] * X
    third = [0] * X
    fourth = [0] * X

    for i, row in data.iterrows():
        x = data.at[i, "u'"] * data.at[i, "w'"]
        if x < 0:
            x = x * -1

        y = x / value
        z = int(y)
        if data.at[i, "u'"] > 0 and data.at[i, "w'"] > 0:
            first[z] = 1
        if data.at[i, "u'"] < 0 and data.at[i, "w'"] > 0:
            second[z] = 1
        if data.at[i, "u'"] < 0 and data.at[i, "w'"] < 0:
            third[z] = 1
        if data.at[i, "u'"] > 0 and data.at[i, "w'"] < 0:
            fourth[z] = 1

    for i in range(X):
        if first[X - i - 1] != 0:
            data.at[index, "Q1_K_Value"] = X - i
            break

    for i in range(X):
        if second[X - i - 1] != 0:
            data.at[index, "Q2_K_Value"] = X - i
            break

    for i in range(X):
        if third[X - i - 1] != 0:
            data.at[index, "Q3_K_Value"] = X - i
            break

    for i in range(X):
        if fourth[X - i - 1] != 0:
            data.at[index, "Q4_K_Value"] = X - i
            break


def octant_ID():
    data["Octant_id"] = 0
    for i in range(N):
        if data.at[i, "u'"] >= 0 and data.at[i, "v'"] >= 0:
            if data.at[i, "w'"] >= 0:
                data.at[i, "Octant_id"] = 1
            if data.at[i, "w'"] < 0:
                data.at[i, "Octant_id"] = -1

        if data.at[i, "u'"] < 0 and data.at[i, "v'"] >= 0:
            if data.at[i, "w'"] >= 0:
                data.at[i, "Octant_id"] = 2
            if data.at[i, "w'"] < 0:
                data.at[i, "Octant_id"] = -2

        if data.at[i, "u'"] < 0 and data.at[i, "v'"] < 0:
            if data.at[i, "w'"] >= 0:
                data.at[i, "Octant_id"] = 3
            if data.at[i, "w'"] < 0:
                data.at[i, "Octant_id"] = -3

        if data.at[i, "u'"] >= 0 and data.at[i, "v'"] < 0:
            if data.at[i, "w'"] >= 0:
                data.at[i, "Octant_id"] = 4
            if data.at[i, "w'"] < 0:
                data.at[i, "Octant_id"] = -4


def octant_column():
    data["Octant_plus_1"] = data["Octant_minus_1"] = ""
    data["Octant_plus_2"] = data["Octant_minus_2"] = ""
    data["Octant_plus_3"] = data["Octant_minus_3"] = ""
    data["Octant_plus_4"] = data["Octant_minus_4"] = ""
    data["Total_Octant_sample"] = ""

    data["Probability_Octant_plus_1"] = data["Probability_Octant_minus_1"] = ""
    data["Probability_Octant_plus_2"] = data["Probability_Octant_minus_2"] = ""
    data["Probability_Octant_plus_3"] = data["Probability_Octant_minus_3"] = ""
    data["Probability_Octant_plus_4"] = data["Probability_Octant_minus_4"] = ""

    data["Min_Octant_Count"] = data["Min_Octant_Count_id"] = ""
    data["Max_Octant_Count"] = data["Max_Octant_Count_id"] = ""

    data.at[index, "Min_Octant_Count"] = data.at[index, "Min_Octant_Count_id"] = N
    data.at[index, "Max_Octant_Count"] = data.at[index, "Max_Octant_Count_id"] = 0


def max_min_update(i, j):
    if data.at[index, "Min_Octant_Count"] > i:
        data.at[index, "Min_Octant_Count"] = i
        data.at[index, "Min_Octant_Count_id"] = j
    if data.at[index, "Max_Octant_Count"] < i:
        data.at[index, "Max_Octant_Count"] = i
        data.at[index, "Max_Octant_Count_id"] = j


def octant():
    octant_ID()
    octant_column()

    # add all octant value with 4 to make it positive to store data in array
    # {-4,0},{-3,1},{-2,2},{-1,3},{NaN,4},{1,5},{2,6},{3,7},{4,8}
    octant_values_frequency = [0] * 9  # array of size 9
    for i in range(N):
        x = data.at[i, "Octant_id"]
        octant_values_frequency[x + 4] += 1

    # for id 1
    data.at[index, "Octant_plus_1"] = octant_values_frequency[1 + 4]
    data.at[index, "Probability_Octant_plus_1"] = round(
        octant_values_frequency[1 + 4] / N, 8
    )
    max_min_update(octant_values_frequency[1 + 4], 1)

    # for id -1
    data.at[index, "Octant_minus_1"] = octant_values_frequency[-1 + 4]
    data.at[index, "Probability_Octant_minus_1"] = round(
        octant_values_frequency[-1 + 4] / N, 8
    )
    max_min_update(octant_values_frequency[-1 + 4], -1)

    # for id 2
    data.at[index, "Octant_plus_2"] = octant_values_frequency[2 + 4]
    data.at[index, "Probability_Octant_plus_2"] = round(
        octant_values_frequency[2 + 4] / N, 8
    )
    max_min_update(octant_values_frequency[2 + 4], 2)

    # for id -2
    data.at[index, "Octant_minus_2"] = octant_values_frequency[-2 + 4]
    data.at[index, "Probability_Octant_minus_2"] = round(
        octant_values_frequency[-2 + 4] / N, 8
    )
    max_min_update(octant_values_frequency[-2 + 4], -2)

    # for id 3
    data.at[index, "Octant_plus_3"] = octant_values_frequency[3 + 4]
    data.at[index, "Probability_Octant_plus_3"] = round(
        octant_values_frequency[3 + 4] / N, 8
    )
    max_min_update(octant_values_frequency[3 + 4], 8)

    # for id -3
    data.at[index, "Octant_minus_3"] = octant_values_frequency[-3 + 4]
    data.at[index, "Probability_Octant_minus_3"] = round(
        octant_values_frequency[-3 + 4] / N, 8
    )
    max_min_update(octant_values_frequency[-3 + 4], -3)

    # for id 4
    data.at[index, "Octant_plus_4"] = octant_values_frequency[4 + 4]
    data.at[index, "Probability_Octant_plus_4"] = round(
        octant_values_frequency[4 + 4] / N, 8
    )
    max_min_update(octant_values_frequency[4 + 4], 4)

    # for id -4
    count_i = 0
    data.at[index, "Octant_minus_4"] = octant_values_frequency[-4 + 4]
    data.at[index, "Probability_Octant_minus_4"] = round(
        octant_values_frequency[-4 + 4] / N, 8
    )
    max_min_update(octant_values_frequency[-4 + 4], -4)

    # total octant
    data.at[index, "Total_Octant_sample"] = N


def allfunction():
    useful_values()
    fk()
    Q_K_Value()
    octant()


def find_std():
    data["U_std"] = data["V_std"] = data["W_std"] = 0.0
    data.at[0, "U_std"] = data["FILTERED_U"].std()
    data.at[0, "V_std"] = data["FILTERED_V"].std()
    data.at[0, "W_std"] = data["FILTERED_W"].std()


def find_mean():
    data["U_mean"] = data["V_mean"] = data["W_mean"] = 0.0
    data.at[0, "U_mean"] = data["FILTERED_U"].mean()
    data.at[0, "V_mean"] = data["FILTERED_V"].mean()
    data.at[0, "W_mean"] = data["FILTERED_W"].mean()


def store():
    with open(OUTPUT_PATH, mode="a") as f:
        row = [
            os.path.basename(os.path.realpath(FILE_PATH)),
            data.at[0, "U_mean"],
            data.at[0, "V_mean"],
            data.at[0, "W_mean"],
            data.at[0, "Var_u'"],
            data.at[0, "Var_v'"],
            data.at[0, "Var_w'"],
            data.at[0, "std_u'"],
            data.at[0, "std_v'"],
            data.at[0, "std_w'"],
            data.at[0, "Skewness_u'"],
            data.at[0, "Skewness_v'"],
            data.at[0, "Skewness_w'"],
            data.at[0, "Kurtosis_u'"],
            data.at[0, "Kurtosis_v'"],
            data.at[0, "Kurtosis_w'"],
            data.at[0, "Reynolds_stress_u'v'"],
            data.at[0, "Reynolds_stress_u'w'"],
            data.at[0, "Reynolds_stress_v'w'"],
            data.at[0, "anisotropy"],
            data.at[0, "M30"],
            data.at[0, "M03"],
            data.at[0, "M12"],
            data.at[0, "M21"],
            data.at[0, "fku_2d"],
            data.at[0, "Fku_2d"],
            data.at[0, "fkw_2d"],
            data.at[0, "Fkw_2d"],
            data.at[index, "fku_3d"],
            data.at[index, "Fku_3d"],
            data.at[index, "fkw_3d"],
            data.at[index, "Fkw_3d"],
            data.at[index, "TKE_3D"],
            data.at[0, "Q1_K_Value"],
            data.at[0, "Q2_K_Value"],
            data.at[0, "Q3_K_Value"],
            data.at[0, "Q4_K_Value"],
            0,
            0,
            data.at[0, "Octant_plus_1"],
            data.at[0, "Octant_minus_1"],
            data.at[0, "Octant_plus_2"],
            data.at[0, "Octant_minus_2"],
            data.at[0, "Octant_plus_3"],
            data.at[0, "Octant_minus_3"],
            data.at[0, "Octant_plus_4"],
            data.at[0, "Octant_minus_4"],
            data.at[0, "Total_Octant_sample"],
            data.at[0, "Probability_Octant_plus_1"],
            data.at[0, "Probability_Octant_minus_1"],
            data.at[0, "Probability_Octant_plus_2"],
            data.at[0, "Probability_Octant_minus_2"],
            data.at[0, "Probability_Octant_plus_3"],
            data.at[0, "Probability_Octant_minus_3"],
            data.at[0, "Probability_Octant_plus_4"],
            data.at[0, "Probability_Octant_minus_4"],
            data.at[0, "Min_Octant_Count"],
            data.at[0, "Min_Octant_Count_id"],
            data.at[0, "Max_Octant_Count"],
            data.at[0, "Max_Octant_Count_id"],
            data.at[0, "K"],
            data.at[0, "TI"],
        ]
        f.write(",".join(str(i) for i in row))
        f.write("\n")


def compute_stats(file_path, write_to_file=True):
    global FILE_PATH
    FILE_PATH = file_path
    global data
    data = pd.read_csv(file_path)
    if ("RAW_U" in data.columns) and ("RAW_V" in data.columns) and ("RAW_W" in data.columns):
        # to be compatible with raw file
        data.rename(
            columns={
                "RAW_U": "FILTERED_U",
                "RAW_V": "FILTERED_V",
                "RAW_W": "FILTERED_W",
            },
            inplace=True,
        )
    global N
    N = len(data)
    find_mean()
    find_std()
    allfunction()
    if write_to_file:
        store()
    return [
        ["Mean", data.at[0, "U_mean"], data.at[0, "V_mean"], data.at[0, "W_mean"]],
        ["Variance", data.at[0, "Var_u'"], data.at[0, "Var_v'"], data.at[0, "Var_w'"]],
        [
            "Skewness",
            data.at[0, "Skewness_u'"],
            data.at[0, "Skewness_v'"],
            data.at[0, "Skewness_w'"],
        ],
        [
            "Kurtosis",
            data.at[0, "Kurtosis_u'"],
            data.at[0, "Kurtosis_v'"],
            data.at[0, "Kurtosis_w'"],
        ],
        [
            ["U'V'", "U'W'", "V'W'"],
            data.at[0, "Reynolds_stress_u'v'"],
            data.at[0, "Reynolds_stress_u'w'"],
            data.at[0, "Reynolds_stress_v'w'"],
        ],
    ]


if __name__ == "__main__":
    FILE_PATH = sys.argv[1]
    compute_stats(FILE_PATH)
