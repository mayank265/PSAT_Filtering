# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 22:08:23 2023

@author: Sanjit
"""

import glob
import pandas as pd

files = [file for file in glob.glob('Files to process/*.csv')]

resDF = pd.DataFrame(columns=['fileName','Median_U','Mean_U','Standard Deviation_U', 'Skewnewss_U','Kurtosis_U',\
                              'Median_V','Mean_V','Standard Deviation_V', 'Skewnewss_V','Kurtosis_V',\
                                  'Median_W','Mean_W','Standard Deviation_W', 'Skewnewss_W','Kurtosis_W'])

for i, file in enumerate(files):
    resDF.at[i,'fileName'] = file.split('\\')[1][:-4]
    if(file.split('\\')[1][:-4] == '2.9_cm20140611204525_Full_Raw_file_Orig'):
        tempDF = pd.read_csv(file)
        for c in ['U', 'V', 'W']:
            resDF.at[i,'Median_'+c] = round(tempDF['RAW_'+c].median(),8) #median
            resDF.at[i,'Mean_'+c] = round(tempDF['RAW_'+c].mean(),8) #mean
            resDF.at[i,'Standard Deviation_'+c] = round(tempDF['RAW_'+c].std(),8) #standard deviation
            resDF.at[i,'Skewnewss_'+c] = round(tempDF['RAW_'+c].skew(),8) #skewnewss
            resDF.at[i,'Kurtosis_'+c] = round(tempDF['RAW_'+c].kurt(),8) #kurtosis
            
    else:
        tempDF = pd.read_csv(file)
        for c in ['U', 'V', 'W']:
            resDF.at[i,'Median_'+c] = round(tempDF['FILTERED_'+c].median(),8) #median
            resDF.at[i,'Mean_'+c] = round(tempDF['FILTERED_'+c].mean(),8) #mean
            resDF.at[i,'Standard Deviation_'+c] = round(tempDF['FILTERED_'+c].std(),8) #standard deviation
            resDF.at[i,'Skewnewss_'+c] = round(tempDF['FILTERED_'+c].skew(),8) #skewnewss
            resDF.at[i,'Kurtosis_'+c] = round(tempDF['FILTERED_'+c].kurt(),8) #kurtosis
        
resDF.to_excel('Files to process/Results.xlsx',index=False)