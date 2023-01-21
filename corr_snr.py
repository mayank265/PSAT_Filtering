import csv


def Replace(Data, BaseColumns, Columns, THRESHOLD):
    for i in range(1, len(Data) - 1):
        modify_row = False
        for j in BaseColumns:
            if Data[i][j] < THRESHOLD:
                modify_row = True
        if modify_row:
            for j in Columns:
                Data[i][j] = round((Data[i - 1][j] + Data[i + 1][j]) / 2, 5)


def Replace_AVG(Data, BaseColumns, Columns, THRESHOLD):
    for i in range(1, len(Data) - 1):
        AVG = 0
        for j in BaseColumns:
            AVG += Data[i][j]
        AVG /= len(BaseColumns)
        if AVG < THRESHOLD:
            for j in Columns:
                Data[i][j] = round((Data[i - 1][j] + Data[i + 1][j]) / 2, 5)


def Replace_SNR(Data, THRESHOLD):
    Replace(Data, [11, 12, 13], [3, 4, 5], THRESHOLD)


def Replace_CORR(Data, THRESHOLD):
    Replace(Data, [15, 16, 17], [3, 4, 5], THRESHOLD)


def Replace_AVG_SNR(Data, THRESHOLD):
    Replace(Data, [11, 12, 13], [3, 4, 5], THRESHOLD)


def Replace_AVG_CORR(Data, THRESHOLD):
    Replace(Data, [15, 16, 17], [3, 4, 5], THRESHOLD)


def main():

    SNR_THRESHOLD = 20
    CORR_THRESHOLD = 70

    # with open('Data.csv', 'r') as f:
    FILE = "2.9_cm20140611204525_Full_Raw_file_Orig.csv"
    with open(FILE, "r") as f:
        reader = csv.reader(f)
        Data = [row for row in reader]

    Headers = Data[0].copy()
    print(Data[:5])
    Data = Data[1:]
    for i in range(len(Data)):
        for j in range(len(Data[i])):
            Data[i][j] = float(Data[i][j])

    print(
        """
        Choose your choice:

        1) Minimum SNR
        2) Minimum Corr
        3) Average SNR
        4) Average Corr

        Choose (1) or (2):
        """
    )
    choice = input()
    if choice == "1":
        Replace_SNR(Data, SNR_THRESHOLD)
        filename1 = FILE[:-4] + "Filtered_" + f"Min_SNR_{SNR_THRESHOLD}.csv"
    elif choice == "2":
        Replace_CORR(Data, CORR_THRESHOLD)
        filename1 = FILE[:-4] + "Filtered_" + f"Min_Correlation_{CORR_THRESHOLD}.csv"
    elif choice == "3":
        Replace_AVG_SNR(Data, SNR_THRESHOLD)
        filename1 = FILE[:-4] + "Filtered_" + f"Average_SNR_{SNR_THRESHOLD}.csv"
    elif choice == "4":
        Replace_AVG_CORR(Data, CORR_THRESHOLD)
        filename1 = (
            FILE[:-4] + "Filtered_" + f"Average_Correlation_{CORR_THRESHOLD}.csv"
        )

    COLUMNS = [0, 3, 4, 5]
    with open(filename1, "w", newline="") as f:
        writer = csv.writer(f)
        row_data = []
        for j in COLUMNS:
            row_data.append(Headers[j])
        writer.writerow(row_data)
        for row in Data:
            row_data = []
            for j in COLUMNS:
                row_data.append(row[j])
            writer.writerow(row_data)


if __name__ == "__main__":
    main()
