import pandas as pd
import os 
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles

## get COVID-19 fatality time-series data
url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv'
us = pd.read_csv(url)

# process the SafeGraph mobility data
# substitute '/Users/kpele/Documents/SafeGraph/' with your own directory where the data are stored
directory_sd = "/Users/kpele/Documents/SafeGraph/social-distancing/v2/2020/"
files = getListOfFiles(directory_sd)

stay_home_pcg = dict()

for f in files: 
        print(f)
        if '.DS_Store' in f:
                continue
        tmp = pd.read_csv(f,compression="gzip")
	# since the recording of cases started 01-21-2020 we do not need the mobility data prior to that
        if tmp.iloc[0]['date_range_start'].rsplit("T")[0] < '2020-01-21':
            pass
        try:
            stay_home_pcg[tmp.iloc[0]['date_range_start'].rsplit("T")[0]] = np.average(tmp['median_percentage_time_home'], weights=tmp['device_count'])
        except:
            print(tmp.head())

stay_home_pcg = {key:val for key, val in stay_home_pcg.items() if key > '2020-01-20'}
stay_home_pcg = {key:val for key, val in stay_home_pcg.items() if key < '2020-06-03'}

mobility = []

for i in range(len(stay_home_pcg)):
    try:
        mobility.append(stay_home_pcg[us.iloc[i]['date']])
    except:
        pass

granger_data= us[us['date'] < '2020-06-03']
granger_data['mobility'] = mobility

diff_deaths = [0]+[granger_data.iloc[i]['deaths']-granger_data.iloc[i-1]['deaths'] for i in range(1,len(granger_data))]
granger_data['daily_deaths'] = diff_deaths
diff_cases = [0]+[granger_data.iloc[i]['cases']-granger_data.iloc[i-1]['cases'] for i in range(1,len(granger_data))]
granger_data['daily_cases'] = diff_cases

# aggregate data weekly
# week indices
d = [0,7,14,21,28,35,42,49,56,63,70,77,84,91,98,105,112,119, 126, 133]

weekly_deaths = []
weekly_mobility = []

for i in range(1,len(d)):
    weekly_deaths.append(sum(granger_data.iloc[d[i-1]:d[i]]['daily_deaths']))
    weekly_mobility.append(np.mean(granger_data.iloc[d[i-1]:d[i]]['mobility']))
    
    
weekly_granger = pd.DataFrame(list(zip(weekly_deaths, weekly_mobility)), columns =['deaths', 'mobility']) 
weekly_granger.to_csv("granger_ts.csv",index=False)
