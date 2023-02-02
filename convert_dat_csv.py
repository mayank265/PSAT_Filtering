import pandas as pd
import pandas as pd
from pathlib import Path
import glob


fileList = glob.glob("./INPUT_DIR/*.dat")
files = fileList.readlines()
for file in files:
    base = Path(file).stem.strip()
    output_csv = file[:-4] + ".csv"

    header_list = [
        "Time",
        "SL",
        "counter",
        "RAW_U",
        "RAW_V",
        "RAW_W",
        "RAW_W1",
        "AMP-U",
        "AMP-V",
        "AMP-W",
        "AMP-W1",
        "SNR_U",
        "SNR_V",
        "SNR_W",
        "SNR-W1",
        "Corr_U",
        "Corr_V",
        "Corr_W",
        "Corr-W1",
    ]
    dataframe = pd.read_csv(file, delimiter=" +", engine="python")
    dataframe.to_csv(output_csv, encoding="utf-8", header=header_list, index=False)
