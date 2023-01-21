from matplotlib import pyplot as plt
import csv

def Get_next_Good(Data, Iterator, Column, THRESHOLD):
    for i in range(Iterator, len(Data)):
        if (Data[i][Column] >= THRESHOLD):
            return i


def Replace(Data, BaseColumn, Column, THRESHOLD):
    PREV = -1
    for i in range(len(Data)):
        if (Data[i][BaseColumn] >= THRESHOLD):
            PREV = i
        else:
            NEXT = Get_next_Good(Data, i, BaseColumn, THRESHOLD)
            if (PREV != -1) and NEXT:
                Data[i][BaseColumn] = round((Data[PREV][BaseColumn] + Data[NEXT][BaseColumn]) / 2, 5)
                Data[i][Column] = round((Data[PREV][Column] + Data[NEXT][Column]) / 2, 5)
            else:
                if (PREV == -1):
                    NEXT = Get_next_Good(Data, i, BaseColumn, THRESHOLD)
                    Data[i][BaseColumn] = Data[NEXT][BaseColumn]
                    Data[i][Column] = Data[NEXT][Column]
                elif not NEXT:
                    Data[i][BaseColumn] = Data[PREV][BaseColumn]
                    Data[i][Column] = Data[PREV][Column]


def Replace_SNR(Data, THRESHOLD):
    Replace(Data, 11, 3, THRESHOLD)
    Replace(Data, 12, 4, THRESHOLD)
    Replace(Data, 13, 5, THRESHOLD)

def Replace_CORR(Data, THRESHOLD):
    Replace(Data, 15, 3, THRESHOLD)
    Replace(Data, 16, 4, THRESHOLD)
    Replace(Data, 17, 5, THRESHOLD)

def main():

    SNR_THRESHOLD = 15
    CORR_THRESHOLD = 70

   
    # with open('Data.csv', 'r') as f:
    with open('2.9_cm20140611204525_Full_Raw_file_Orig.csv', 'r') as f:
        reader = csv.reader(f)
        Data = [row for row in reader]

    Headers = Data[0].copy()
    print(Data[:5])
    Data = Data[1:]
    for i in range(len(Data)):
        for j in range(len(Data[i])):
            Data[i][j] = float(Data[i][j])
    
    PLOT_DATA = []
    T = [round(float(Data[i][0]), 2) for i in range(len(Data))]
    PLOT_DATA.append(T)
    U = [round(float(Data[i][3]), 2) for i in range(len(Data))]
    PLOT_DATA.append(U)

    print(
        """
        Choose your choice:

        1) Minimum SNR

        2) Minimum Corr

        Choose (1) or (2):
        """
    )
    choice = input()
    if (choice == '1'):
        Replace_SNR(Data, SNR_THRESHOLD)
        filename1 = "Data_SNR.csv"
    elif (choice == '2'):
        Replace_CORR(Data, CORR_THRESHOLD)
        filename1 = "Data_Corr.csv"
    
    with open(filename1, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(Headers)
        writer.writerows(Data)
    

if __name__ == '__main__':
    main()
