import pandas as pd 
import math
import os
import ntpath
import glob
import pandas as pd
import numpy as np
import datetime
from pathlib import Path 
from datetime import datetime 


fileList = open('input_file_list.txt', 'r')
files = fileList.readlines()
for file in files:
    input_filename = file.strip()
    
    base = (Path(input_filename).stem.strip())
    output_csv = base+".csv"
    
    header_list = ['Time','SL' ,'counter' ,'RAW_U','RAW_V','RAW_W','RAW_W1','AMP-U' ,'AMP-V' ,'AMP-W' ,'AMP-W1' ,'SNR_U','SNR_V','SNR_W','SNR-W1' ,'Corr_U','Corr_V','Corr_W','Corr-W1']
    dataframe = pd.read_csv(input_filename,delimiter=" +", engine='python')
    dataframe.to_csv(output_csv, encoding='utf-8', header=header_list, index=False)
