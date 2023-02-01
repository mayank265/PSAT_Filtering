import os
from copy import deepcopy
import csv
import numpy as np
from datetime import datetime
from statistics import stdev
from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt, Confirm
from rich import print as rprint
from stats import compute_stats


class DetectReplaceSpikes:
    def __init__(
        self,
        FILEPATH,
        CORR_THRESHOLD,
        SNR_THRESHOLD,
        VELOCITY_MULTIPLIER,
        CORR_COLS=[15, 16, 17],
        SNR_COLS=[11, 12, 13],
        VELOCITY_COLS=[3, 4, 5],
        EXPORT_COLS=[0, 3, 4, 5],
        HEADERS=["TIME", "FILTERED_U", "FILTERED_V", "FILTERED_W"],
    ) -> None:
        self.CORR_THRESHOLD = CORR_THRESHOLD
        self.SNR_THRESHOLD = SNR_THRESHOLD
        self.VELOCITY_MULTIPLIER = VELOCITY_MULTIPLIER
        self.DATA, self.BASE_FILE_NAME, self.DIRECTORY = read_file(FILEPATH)
        self.working_data = None
        self.CORR_COLS = CORR_COLS
        self.SNR_COLS = SNR_COLS
        self.VELOCITY_COLS = VELOCITY_COLS

        self.STD_DEV = {}  # calculating stdev for velocity cols is enough for now
        for col in VELOCITY_COLS:
            tmp_col_data = []
            for row in self.DATA:
                tmp_col_data.append(row[col])
            self.STD_DEV[col] = stdev(tmp_col_data)

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
            self.abs_velocity_threshold,
        ]
        self.DETECTION_LABELS = [
            "Minimum SNR",
            "Minimum Correlation",
            "Average SNR",
            "Average Correlation",
            "Min Correlation & Min SNR",
            "Min Correlation & Average SNR",
            "Average Correlation & Min SNR",
            "Average Correlation & Average SNR",
            "Velocity Threshold",
            "Absolute Velocity Threshold",
        ]

        # Calculating Column means for further use
        COLUMN_COUNT = len(self.DATA[0])
        self.COL_MEANS = [0] * COLUMN_COUNT
        for i in range(COLUMN_COUNT):
            AVG = 0
            for row in self.DATA:
                AVG += row[i]
            AVG /= len(self.DATA)
            self.COL_MEANS[i] = AVG
        self.VELOCITY_COLS = VELOCITY_COLS

        self.replacement_methods = [
            [self.f1, "R1"],
            [self.f2, "R2"],
            [self.f3, "R3"],
            [self.f4, "R4"],
            [self.f5, "R5"],
        ]
        self.REPLACEMENT_LABELS = [
            "extrapolation from the preceding data point",
            "extrapolation from the two preceding points",
            "the overall mean of the signal",
            "a smoothed estimate",
            "interpolation between the ends of the spike",
        ]

        self.EXPORT_COLS = EXPORT_COLS
        self.HEADERS = HEADERS

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

    def check_abs_velocity_threshold(self, row, multiplier):
        spikes = 0
        for col in self.VELOCITY_COLS:
            if abs(row[col]) > multiplier * abs(self.STD_DEV[col]):
                spikes += 1
        return spikes >= 2

    def detect_and_replace(self, conditions, replacement_method, file_suffix):
        """
        conditions is a list of list of two objects:
        - function
        - args to the function
        For every row in the Data, we call all the functions in 'conditions' list.
        If all of them returns True for that row, we run replacement method on that row.
        To summarize, we check AND of all conditions in 'conditions' list.
        """
        replaced_rows = 0
        self.working_data = deepcopy(self.DATA)
        for i, row in enumerate(self.working_data):
            all_True = True
            for condition in conditions:
                if not condition[0](*([row] + condition[1])):
                    all_True = False
            if all_True:
                replaced_rows += 1
                replacement_method[0](i)
        print(f"{replaced_rows} row(s) replaced.")
        file_suffix = file_suffix + "_" + replacement_method[1]
        self.write_to_file(file_suffix)

        self.working_data = None

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

    def abs_velocity_threshold(self, replacement_method):
        return self.detect_and_replace(
            [[self.check_abs_velocity_threshold, [self.VELOCITY_MULTIPLIER]]],
            replacement_method,
            f"abs_v_threshold_{self.VELOCITY_MULTIPLIER}",
        )

    def f1(self, row_index):
        for j in self.VELOCITY_COLS:
            try:
                self.working_data[row_index][j] = self.working_data[row_index - 1][j]
            except:
                self.working_data[row_index][j] = self.working_data[row_index][j]

    def f2(self, row_index):
        for j in self.VELOCITY_COLS:
            try:
                self.working_data[row_index][j] = (
                    2 * self.working_data[row_index - 1][j]
                    - self.working_data[row_index - 2][j]
                )
            except:
                self.working_data[row_index][j] = self.working_data[row_index][j]

    def f3(self, row_index):
        for j in self.VELOCITY_COLS:
            self.working_data[row_index][j] = self.COL_MEANS[j]

    def f4(self, row_index):
        # TODO
        for j in self.VELOCITY_COLS:
            self.working_data[row_index][j] = self.working_data[row_index][j]

    def f5(self, row_index):
        for j in self.VELOCITY_COLS:
            try:
                self.working_data[row_index][j] = round(
                    (
                        self.working_data[row_index - 1][j]
                        + self.working_data[row_index + 1][j]
                    )
                    / 2,
                    5,
                )
            except IndexError:
                self.working_data[row_index][j] = self.working_data[row_index][j]

    def write_to_file(self, file_suffix):
        DATE_SUFFIX = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        OUTPUT_FILE = os.path.join(
            self.DIRECTORY, f"{self.BASE_FILE_NAME}_{file_suffix}_{DATE_SUFFIX}.csv"
        )
        with open(OUTPUT_FILE, "w") as f:
            writer = csv.writer(f)
            writer.writerow(self.HEADERS)  # header
            for row in self.working_data:
                row_data = []
                for j in self.EXPORT_COLS:
                    row_data.append(row[j] * 100)
                writer.writerow(row_data)

        print(f"written to {OUTPUT_FILE}")
        # if Confirm.ask("Compute statistics on this output file?", default=True):
            # compute_stats(OUTPUT_FILE)
        # Force Compute Stats 
        compute_stats(OUTPUT_FILE) 

    def process_choices(self, detection_choice, replacement_choice):
        DETECTIONS = len(self.detection_methods)
        REPLACEMENTS = len(self.replacement_methods)
        if detection_choice == DETECTIONS and replacement_choice == REPLACEMENTS:
            for i in range(DETECTIONS):
                for j in range(REPLACEMENTS):
                    self.detection_methods[i](self.replacement_methods[j])
        elif detection_choice == DETECTIONS and (
            0 <= replacement_choice < REPLACEMENTS
        ):
            for i in range(DETECTIONS):
                self.detection_methods[i](self.replacement_methods[replacement_choice])
        elif (
            0 <= detection_choice < DETECTIONS
        ) and replacement_choice == REPLACEMENTS:
            for j in range(REPLACEMENTS):
                self.detection_methods[detection_choice](self.replacement_methods[j])
        elif (0 <= detection_choice < DETECTIONS) and (
            0 <= replacement_choice < REPLACEMENTS
        ):
            self.detection_methods[detection_choice](
                self.replacement_methods[replacement_choice]
            )
        else:
            print("Choose the input properly.")


def read_file(filepath):
    """
    Reads a CSV file and returns following objects
    - List of lists (floats)
    - Base filename (used for writing)
    - directory"""
    DIRECTORY = os.path.dirname(os.path.realpath(filepath))
    BASE_FILE_NAME = os.path.splitext(os.path.basename(os.path.realpath(filepath)))[0]
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        DATA = [row for row in reader]

    DATA = DATA[1:]  # removing header
    for i in range(len(DATA)):
        for j in range(len(DATA[i])):
            DATA[i][j] = float(DATA[i][j])
    return DATA, BASE_FILE_NAME, DIRECTORY


def get_user_input(DETECTION_LABELS, REPLACEMENT_LABELS):
    """
    Fetches user input and returns two integers
    """
    DETECTION_METHODS_COUNT = len(DETECTION_LABELS)
    REPLACEMENT_METHODS_COUNT = len(REPLACEMENT_LABELS)
    console = Console()

    table = Table(title="Detection methods")
    table.add_column("Method", justify="center", style="cyan")
    table.add_column("Choice", justify="right", style="magenta")
    for index, method in enumerate(DETECTION_LABELS):
        table.add_row(method, str(index))
    table.add_row("Run all methods", str(DETECTION_METHODS_COUNT))

    console.print(table)
    while True:
        detection_choice = IntPrompt.ask(
            f":rocket: Choose a method from above (between [b]0[/b] and [b]{DETECTION_METHODS_COUNT}[/b])",
            default=0,
        )
        if 0 <= detection_choice <= DETECTION_METHODS_COUNT:
            break
        else:
            rprint(
                f":pile_of_poo: [prompt.invalid]Number must be between 0 and {DETECTION_METHODS_COUNT}"
            )

    table = Table(title="Replacement methods")
    table.add_column("Method", justify="center", style="cyan")
    table.add_column("Choice", justify="right", style="magenta")
    for index, method in enumerate(REPLACEMENT_LABELS):
        table.add_row(method, str(index))
    table.add_row("Run all methods", str(REPLACEMENT_METHODS_COUNT))
    console.print(table)

    while True:
        replacement_choice = IntPrompt.ask(
            f":rocket: Choose a method from above (between [b]0[/b] and [b]{REPLACEMENT_METHODS_COUNT}[/b])",
            default=0,
        )
        if 0 <= replacement_choice <= REPLACEMENT_METHODS_COUNT:
            break
        else:
            rprint(
                f":pile_of_poo: [prompt.invalid]Number must be between 0 and {REPLACEMENT_METHODS_COUNT}"
            )
    return detection_choice, replacement_choice


def main():
    INPUT_FILE = "2.9_cm20140611204525_Full_Raw_file_Orig.csv"

    SNR_THRESHOLD = 20
    CORR_THRESHOLD = 70
    VELOCITY_MULTIPLIER = 1.5
    CORR_COLS = [15, 16, 17]
    SNR_COLS = [11, 12, 13]
    RAW_COLS = [3, 4, 5]
    EXPORT_COLS = [0, 3, 4, 5]
    OUTPUT_HEADERS = ["TIME", "FILTERED_U", "FILTERED_V", "FILTERED_W"]
    model = DetectReplaceSpikes(
        INPUT_FILE,
        CORR_THRESHOLD,
        SNR_THRESHOLD,
        VELOCITY_MULTIPLIER,
        CORR_COLS,
        SNR_COLS,
        RAW_COLS,
        EXPORT_COLS,
        OUTPUT_HEADERS,
    )
    detection_choice, replacement_choice = get_user_input(
        model.DETECTION_LABELS, model.REPLACEMENT_LABELS
    )
    model.process_choices(detection_choice, replacement_choice)


if __name__ == "__main__":
    main()
