import pandas as pd
import pandas
import os
import numpy as np
import geocoder
import json
import gzip

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


directory_sd = "/Users/kpele/Documents/SafeGraph/social-distancing/v2/2020/"

files = getListOfFiles(directory_sd)

# obtain data for February mobility and March mobility

for f in files[31:62]+files[95:125]:
	print(f)
	if '.DS_Store' in f:
		continue
	tmp = pd.read_csv(f,compression="gzip")
	#tmp = x[(x['origin_census_block_group']>= 420000000000) & (x['origin_census_block_group']<= 429999999999)]
	if f == files[31]:
		x_pa = tmp
	else:
		x_pa = pd.concat([x_pa,tmp],sort=False)


x = x_pa
new = x['date_range_start'].str.split("T",n=1,expand = True)
x['date_range_start'] = new[0]
home_stay_pcg = pandas.DataFrame(columns = ['origin_census_block_group'], index= list(x['origin_census_block_group'].unique()))
home_stay_pcg['origin_census_block_group'] = list(x['origin_census_block_group'].unique())

#home_stay_pcg = pandas.DataFrame(columns = list(x['date_range_start'].unique()), index= list(x['origin_census_block_group'].unique())) 
#devices_count = pandas.DataFrame(columns = list(x['date_range_start'].unique()), index= list(x['origin_census_block_group'].unique())) 

# get the median percentage of time spent at home

for d in list(x['date_range_start'].unique()):
	print(d)
	tmp = x[x['date_range_start'] == d].reset_index()
	tmp_df = pandas.DataFrame(list(zip(list(tmp['origin_census_block_group']), list(tmp['median_percentage_time_home']))),columns=['origin_census_block_group',tmp['date_range_start'][0]])
	#tmp2_df = pandas.DataFrame(list(zip(list(tmp['origin_census_block_group']), list(tmp['distance_traveled_from_home']))),columns=['origin_census_block_group',tmp['date_range_start'][0]])
	home_stay_pcg = home_stay_pcg.merge(tmp_df,on="origin_census_block_group",how="inner")
	#dist_traveled = dist_traveled.merge(tmp2_df,on="origin_census_block_group",how="inner")
	#for b in range(len(tmp)):
	#	home_stay_pcg.loc[tmp['origin_census_block_group'][b],d] = tmp['median_percentage_time_home'][b] 
	#	devices_count.loc[tmp['origin_census_block_group'][b],d] = tmp['device_count'][b] 

# write the files to excel


home_stay_pcg.to_csv("home_stay_tmp.csv",index=False)

## find fraction of population less than 50 yo 

# census variables for more than 50 (male and female)
fields_more50 = ['B01001m40','B01001m41','B01001m42','B01001m43','B01001m44','B01001m45','B01001m46','B01001m47','B01001m48','B01001m49','B01001m16','B01001m17','B01001m18','B01001m19','B01001m20','B01001m21','B01001m22','B01001m23','B01001m24','B01001m25']
field_total = ['B01001e2','B01001e26']
fields_hispanic = 'B03002e12'
fields_white = 'B02001e2'
fields_black = 'B02001e3'
fields_nativeAmericans = ['B02001e4','B02001e6','B02001e7']
fields_asian = 'B02001e5'
fields_raceTot = 'B02001e1'
fields_income = 'B19013e1'

cbg_b01 = pd.read_csv("/Users/kpele/Documents/SafeGraph/safegraph_open_census_data/data/cbg_b01.csv") 

tmp1 = cbg_b01[fields_more50].sum(axis=1)
tmp2 = cbg_b01[field_total].sum(axis=1)
tmp_index = [t for t in cbg_b01['census_block_group']]

cbg_b19 = pd.read_csv("/Users/kpele/Documents/SafeGraph/safegraph_open_census_data/data/cbg_b19.csv")
tmpIncome = cbg_b19[fields_income]

demo_data = pd.DataFrame(list(zip(tmp_index,list(tmp1/tmp2),tmpIncome)), columns = ['census_block_group','pcg_older_50','median_income'])
demo_data.to_csv("demo_data.csv",index=False)


cbg_b02 = pd.read_csv("/Users/kpele/Documents/SafeGraph/safegraph_open_census_data/data/cbg_b02.csv")
cbg_b03 = pd.read_csv("/Users/kpele/Documents/SafeGraph/safegraph_open_census_data/data/cbg_b03.csv")

tmpHispanic = cbg_b03[fields_hispanic]
tmpWhite = cbg_b02[fields_white]
tmpBlack = cbg_b02[fields_black]
tmpNatives = cbg_b02[fields_nativeAmericans].sum(axis=1)
tmpAsian = cbg_b02[fields_asian]
tmpAll = cbg_b02[fields_raceTot]
tmp_indexrace = [t for t in cbg_b02['census_block_group']]

demo_datarace = pd.DataFrame(list(zip(tmp_indexrace,list(tmpHispanic/tmpAll),list(tmpWhite/tmpAll),list(tmpBlack/tmpAll),list(tmpNatives/tmpAll),list(tmpAsian/tmpAll))), columns = ['census_block_group','Hispanic','White','Black','Natives-Others','Asian'])
demo_datarace.to_csv("demo_datarace.csv",index=False)

# use the demo_data and the home_stay_pcg.csv to run a beta regression 
