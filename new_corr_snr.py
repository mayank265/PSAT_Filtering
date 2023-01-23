from copy import deepcopy
import csv
import numpy as np
from datetime import datetime
from statistics import stdev


class DetectSpikes:
    def __init__(
        self,
        Data,
        CORR_THRESHOLD,
        SNR_THRESHOLD,
        VELOCITY_MULTIPLIER,
        CORR_COLS=[15, 16, 17],
        SNR_COLS=[11, 12, 13],
        VELOCITY_COLS=[3, 4, 5],
    ) -> None:
        self.CORR_THRESHOLD = CORR_THRESHOLD
        self.SNR_THRESHOLD = SNR_THRESHOLD
        self.VELOCITY_MULTIPLIER = VELOCITY_MULTIPLIER
        self.Data = Data
        self.CORR_COLS = CORR_COLS
        self.SNR_COLS = SNR_COLS
        self.VELOCITY_COLS = VELOCITY_COLS

        self.STD_DEV = {}  # calculating stdev for velocity cols is enough for now
        for col in VELOCITY_COLS:
            data = []
            for row in self.Data:
                data.append(row[col])
            self.STD_DEV[col] = stdev(data)

        self.detection_methods = [
            self.minimum_CORR,
            self.average_CORR,
            self.minimum_SNR,
            self.average_SNR,
            self.min_CORR_min_SNR,
            self.min_CORR_avg_SNR,
            self.avg_CORR_min_SNR,
            self.avg_CORR_avg_SNR,
            self.velocity_threshold,
        ]

    def check_threshold(self, row, cols, threshold):
        for col in cols:
            if row[col] < threshold:
                return True

    def check_average(self, row, cols, threshold):
        average = 0
        for col in cols:
            average += row[col]
        average /= len(cols)
        return average < threshold

    def check_velocity_threshold(self, row, multiplier):
        normal_sum = 0
        stdev_normal_sum = 0
        for col in self.VELOCITY_COLS:
            normal_sum += row[col]
            stdev_normal_sum += self.STD_DEV[col]
        normal_sum = abs(normal_sum)
        return abs(normal_sum) > multiplier * abs(stdev_normal_sum)

    def detect_and_replace(self, conditions, replacement_method, filename):
        """
        conditions is a list of list of two objects:
        - function
        - args to the function
        For every row in the Data, we call all the functions in 'conditions' list.
        If all of them returns True for that row, we run replacement method on that row.
        To summarize, we check AND of all conditions in 'conditions' list.
        """
        replaced_rows = 0
        for i, row in enumerate(self.Data):
            all_True = True
            for condition in conditions:
                if not condition[0](*([row] + condition[1])):
                    all_True = False
            if all_True:
                replaced_rows += 1
                replacement_method[0](i)
        print(f"{replaced_rows} row(s) replaced.")
        return filename + "_" + replacement_method[1]

    def minimum_CORR(self, replacement_method):
        return self.detect_and_replace(
            [[self.check_threshold, [self.CORR_COLS, self.CORR_THRESHOLD]]],
            replacement_method,
            f"min_CORR_{self.CORR_THRESHOLD}",
        )

    def average_CORR(self, replacement_method):
        return self.detect_and_replace(
            [[self.check_average, [self.CORR_COLS, self.CORR_THRESHOLD]]],
            replacement_method,
            f"avg_CORR_{self.CORR_THRESHOLD}",
        )

    def minimum_SNR(self, replacement_method):
        return self.detect_and_replace(
            [[self.check_threshold, [self.SNR_COLS, self.SNR_THRESHOLD]]],
            replacement_method,
            f"min_SNR_{self.SNR_THRESHOLD}",
        )

    def average_SNR(self, replacement_method):
        return self.detect_and_replace(
            [[self.check_average, [self.SNR_COLS, self.SNR_THRESHOLD]]],
            replacement_method,
            f"avg_SNR_{self.SNR_THRESHOLD}",
        )

    def min_CORR_min_SNR(self, replacement_method):
        return self.detect_and_replace(
            [
                [self.check_threshold, [self.CORR_COLS, self.CORR_THRESHOLD]],
                [self.check_threshold, [self.SNR_COLS, self.SNR_THRESHOLD]],
            ],
            replacement_method,
            f"min_CORR_{self.CORR_THRESHOLD}_min_SNR_{self.SNR_THRESHOLD}",
        )

    def min_CORR_avg_SNR(self, replacement_method):
        return self.detect_and_replace(
            [
                [self.check_threshold, [self.CORR_COLS, self.CORR_THRESHOLD]],
                [self.check_average, [self.SNR_COLS, self.SNR_THRESHOLD]],
            ],
            replacement_method,
            f"min_CORR_{self.CORR_THRESHOLD}_avg_SNR_{self.SNR_THRESHOLD}",
        )

    def avg_CORR_min_SNR(self, replacement_method):
        return self.detect_and_replace(
            [
                [self.check_average, [self.CORR_COLS, self.CORR_THRESHOLD]],
                [self.check_threshold, [self.SNR_COLS, self.SNR_THRESHOLD]],
            ],
            replacement_method,
            f"avg_CORR_{self.CORR_THRESHOLD}_min_SNR_{self.SNR_THRESHOLD}",
        )

    def avg_CORR_avg_SNR(self, replacement_method):
        return self.detect_and_replace(
            [
                [self.check_average, [self.CORR_COLS, self.CORR_THRESHOLD]],
                [self.check_average, [self.SNR_COLS, self.SNR_THRESHOLD]],
            ],
            replacement_method,
            f"avg_CORR_{self.CORR_THRESHOLD}_avg_SNR_{self.SNR_THRESHOLD}",
        )

    def velocity_threshold(self, replacement_method):
        return self.detect_and_replace(
            [[self.check_velocity_threshold, [self.VELOCITY_MULTIPLIER]]],
            replacement_method,
            f"v_threshold_{self.VELOCITY_MULTIPLIER}",
        )


class ReplaceSpikes:
    def __init__(
        self,
        Data,
        RAW_COLS=[3, 4, 5],
    ) -> None:
        self.Data = Data

        # Calculating Column means for further use
        column_count = len(Data[0])
        self.ColMeans = [0] * column_count
        for i in range(column_count):
            AVG = 0
            for row in Data:
                AVG += row[i]
            AVG /= len(Data)
            self.ColMeans[i] = AVG
        self.RAW_COLS = RAW_COLS

        self.replacement_methods = [
            [self.f1, "R1"],
            [self.f2, "R2"],
            [self.f3, "R3"],
            [self.f4, "R4"],
            [self.f5, "R5"],
        ]

    def f1(self, row_index):
        for j in self.RAW_COLS:
            try:
                self.Data[row_index][j] = self.Data[row_index - 1][j]
            except:
                self.Data[row_index][j] = self.Data[row_index][j]

    def f2(self, row_index):
        for j in self.RAW_COLS:
            try:
                self.Data[row_index][j] = (
                    2 * self.Data[row_index - 1][j] - self.Data[row_index - 2][j]
                )
            except:
                self.Data[row_index][j] = self.Data[row_index][j]

    def f3(self, row_index):
        for j in self.RAW_COLS:
            self.Data[row_index][j] = self.ColMeans[j]

    def f4(self, row_index):
        # TODO
        for j in self.RAW_COLS:
            self.Data[row_index][j] = self.Data[row_index][j]

    def f5(self, row_index):
        for j in self.RAW_COLS:
            try:
                self.Data[row_index][j] = round(
                    (self.Data[row_index - 1][j] + self.Data[row_index + 1][j]) / 2, 5
                )
            except IndexError:
                self.Data[row_index][j] = self.Data[row_index][j]


def write_to_file(
    Data, COLS, filename, Headers=["TIME", "FILTERED_U", "FILTERED_V", "FILTERED_W"]
):
    if filename[:-4] != ".csv":
        filename += ".csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(Headers)  # header
        for row in Data:
            row_data = []
            for j in COLS:
                row_data.append(row[j] * 100)
            writer.writerow(row_data)
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + filename
    print(f"written to {filename}")


def main():
    INPUT_FILE = "2.9_cm20140611204525_Full_Raw_file_Orig.csv"
    BASE_FILE_NAME = INPUT_FILE[:-4]
    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f)
        Data = [row for row in reader]

    print(Data[:5])
    Data = Data[1:]
    for i in range(len(Data)):
        for j in range(len(Data[i])):
            Data[i][j] = float(Data[i][j])

    SNR_THRESHOLD = 20
    CORR_THRESHOLD = 70
    VELOCITY_MULTIPLIER = 3
    CORR_COLS = [15, 16, 17]
    SNR_COLS = [11, 12, 13]
    RAW_COLS = [3, 4, 5]

    print(
        """
        Choose your choice:

        0) Minimum SNR
        1) Minimum Correlation
        2) Average SNR
        3) Average Correlation
        4) Min Correlation & Min SNR
        5) Min Correlation & Average SNR
        6) Average Correlation & Min SNR
        7) Average Correlation & Average SNR
        8) Velocity Threshold
        9) All of the above

        Choose (0) to (9):
        """
    )
    detection_choice = int(input())
    if detection_choice < 0 or detection_choice > 9:
        return
    print(
        """
        Choose your choice:

        0) extrapolation from the preceding data point
        1) extrapolation from the two preceding points
        2) the overall mean of the signal
        3) a smoothed estimate
        4) interpolation between the ends of the spike
        5) All of the above

        Choose (0) to (5):
        """
    )
    replacement_choice = int(input())
    if replacement_choice < 0 or replacement_choice > 5:
        return

    if detection_choice == 9 and replacement_choice == 5:
        for i in range(9):
            for j in range(5):
                new_data = deepcopy(Data)
                detection = DetectSpikes(
                    new_data, CORR_THRESHOLD, SNR_THRESHOLD, VELOCITY_MULTIPLIER, CORR_COLS, SNR_COLS
                )
                replacement = ReplaceSpikes(new_data, RAW_COLS)
                filename = detection.detection_methods[i](
                    replacement.replacement_methods[j]
                )
                write_to_file(
                    new_data,
                    [0] + RAW_COLS,
                    BASE_FILE_NAME + "_" + filename,
                    ["TIME", "FILTERED_U", "FILTERED_V", "FILTERED_W"],
                )
        return
    elif detection_choice == 9:
        for i in range(9):
            new_data = deepcopy(Data)
            detection = DetectSpikes(
                new_data, CORR_THRESHOLD, SNR_THRESHOLD, VELOCITY_MULTIPLIER, CORR_COLS, SNR_COLS
            )
            replacement = ReplaceSpikes(new_data, RAW_COLS)
            filename = detection.detection_methods[i](
                replacement.replacement_methods[replacement_choice]
            )
            write_to_file(
                new_data,
                [0] + RAW_COLS,
                BASE_FILE_NAME + "_" + filename,
                ["TIME", "FILTERED_U", "FILTERED_V", "FILTERED_W"],
            )
        return
    elif replacement_choice == 5:
        for j in range(5):
            new_data = deepcopy(Data)
            detection = DetectSpikes(
                new_data, CORR_THRESHOLD, SNR_THRESHOLD, VELOCITY_MULTIPLIER, CORR_COLS, SNR_COLS
            )
            replacement = ReplaceSpikes(new_data, RAW_COLS)
            filename = detection.detection_methods[detection_choice](
                replacement.replacement_methods[j]
            )
            write_to_file(
                new_data,
                [0] + RAW_COLS,
                BASE_FILE_NAME + "_" + filename,
                ["TIME", "FILTERED_U", "FILTERED_V", "FILTERED_W"],
            )
        return

    detection = DetectSpikes(
        Data, CORR_THRESHOLD, SNR_THRESHOLD, VELOCITY_MULTIPLIER, CORR_COLS, SNR_COLS
    )
    replacement = ReplaceSpikes(Data, RAW_COLS)
    filename = detection.detection_methods[detection_choice](
        replacement.replacement_methods[replacement_choice]
    )
    write_to_file(
        Data,
        [0] + RAW_COLS,
        BASE_FILE_NAME + "_" + filename,
        ["TIME", "FILTERED_U", "FILTERED_V", "FILTERED_W"],
    )


if __name__ == "__main__":
    main()
