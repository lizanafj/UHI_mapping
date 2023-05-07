# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 12:05:20 2021

@author: Jesus Lizana

###########################################################

#INPUT Files: 

###########################################################

#Folder: city/data/2_filtered/
    Coordinates_London_2021_CWS_all_QC_G8
    Temperature_London_2021_CWS_all_QC_G8
    
    Coordinates_London_2021_OWS_QC_I5
    Temperature_London_2021_OWS_QC_I5


###########################################################

#EXPECTED OUTPUT files:

###########################################################

#Folder: city/data/3_processed

Final hourly profile - clean and ready for analysis:
    Coordinates_London_2021_CWS_all_QC_G8_proc           #eliminating stations with >10% missing data
    Temperature_London_2021_CWS_all_QC_G8_proc

CDHs:
    Coordinates_London_2021_CWS_all_QC_G8_proc_CDH       #calculating CDD total, night_CDD and daytime_CDD (three new columns)



"""

                   
#%%	

##### PYTHON LIBRARIES

import os
import pandas as pd #biblioteca de manipulación y análisis de datos
import datetime
from datetime import datetime, timedelta
from dateutil import tz

import pytz    # $ pip install pytz
import tzlocal # $ pip install tzlocal

import numpy as np #biblioteca de funciones matemáticas
import json

#Matplotlib
import matplotlib.pyplot as plt #biblioteca de generación de gráficos
from matplotlib.cm import ScalarMappable
plt.style.use('default') #estilo para gráficos en matplotlib
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from matplotlib.dates import date2num
import seaborn as sns

#statistics
import scipy.stats as stats

#Qn scale estimator proposed by Rousseeuw and Croux as an alternative to the MAD (for modified z-score)
from statsmodels.robust.scale import qn_scale as qn #https://www.statsmodels.org/dev/_modules/statsmodels/robust/scale.html

#t-student distribution and normal distribution
from scipy.stats import t
from scipy.stats import norm 

#FOR DISTANCES BETWEEN COORDINATES
from geopy.distance import geodesic

#https://pypi.org/project/suntime/
#library for sunset and sunrise
from suntime import Sun, SunTimeException

#In case you want to get rid of the margin in the whole script, you can use
plt.rcParams['axes.xmargin'] = 0   
plt.rcParams['font.family'] = 'sans-serif'
#plt.rcParams['font.sans-serif'] = 'Tahoma'
#plt.rcParams.update({'font.size': 9})

import dateutil.tz

from dateutil.relativedelta import relativedelta

#Directories
cwd = os.path.dirname(__file__)
os.chdir(cwd)


#%%	

#read json file - input data for extraction
with open('projectdata_p.json', 'r') as fp:
    data = json.load(fp)
  
#%%	  

###########################################################

#INPUT DATA required to select city

###########################################################

city = data["city"]
lat = data["lat"]
long = data["long"]

#timeframe of data available -- month - day - year
first_date=data["first_date"]  
last_date=data["last_date"] 

#Timeframe criteria to eliminate statations with data availability <90%  -- month - day - year
first_date1=data["first_date1"]  
last_date1=data["last_date1"]  

#colors
color_net = data["color_net"]
color_wund =data["color_wund"]
color_ows =data["color_ows"]
color_cws = data["color_cws"]
color_outliers = data["color_outliers"]

#Coordinates for solar path - calculation of day at night hours
latitude = data["lat"]
longitude = data["long"]

#baseline temperature to calculate CDH
baseline_t = 18
#%%

first_date1 = str(datetime.strptime(first_date1, '%d-%m-%Y'))
last_date1 = str(datetime.strptime(last_date1, '%d-%m-%Y'))         
	
#%%
#Project directories   
cwd_main = cwd[0:-16]
cwd_project = cwd_main+fr"\projectname\{city}"	
cwd_project_raw = cwd_main+fr"\projectname\{city}\data\0_raw"
cwd_project_struct = cwd_main+fr"\projectname\{city}\data\1_structured"
cwd_project_filt = cwd_main+fr"\projectname\{city}\data\2_filtered"
cwd_project_proc = cwd_main+fr"\projectname\{city}\data\3_processed"
cwd_project_rep = cwd_main+fr"\projectname\{city}\reports"
cwd_project_fig = cwd_main+fr"\projectname\{city}\reports\figures"


#%%	

######################################################################################################################

#### LOAD FILES 

######################################################################################################################
          
###########################################################

#### LOAD FILES FROM FOLDER 2_qc

###########################################################

#Directory for city selected
os.chdir(cwd_project_filt)

print("Folder opened: ",cwd_project_filt)


CWS_UrbanClimate_all_QC = pd.read_csv("Temperature_London_2021_CWS_all_QC_G8.csv", index_col='date',parse_dates=True) 
CWS_coordinates_all_QC = pd.read_csv("Coordinates_London_2021_CWS_all_QC_G8.csv") 

OWS_Climate_QC = pd.read_csv("Temperature_London_2021_OWS_QC_I5.csv", index_col='date',parse_dates=True) 
OWS_coordinates_QC = pd.read_csv("Coordinates_London_2021_OWS_QC_I5.csv")
   

print("All files have been correctly charged from : ",cwd_project_filt)  
     
#%%	               



######################################################################################################################

#### SELECTION OF DATASETS (STATIONS) WITH nan<10% DURING THE SELECTED PERIOD (first_date1 - last_date1)

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################


###########################################################

# Step 1. Criteria to eliminate stations (eliminate data if nan > 10% in hot days)

###########################################################

CWS_UrbanClimate_all_QC_proc = CWS_UrbanClimate_all_QC.copy()

#Eliminate columns if nan > 10% in hotter weeks (previously check with all year data) 
for col in CWS_UrbanClimate_all_QC_proc.columns: 
    if sum(CWS_UrbanClimate_all_QC_proc.truncate(before=first_date1, after=last_date1)[col].isnull())/float(len(CWS_UrbanClimate_all_QC_proc.truncate(before=first_date1, after=last_date1).index)) > 0.10: 
        del CWS_UrbanClimate_all_QC_proc[col]
        

#%%	

#Percentage of valid values
print("Percentage of values BEFORE quality criteria", 
      100*CWS_UrbanClimate_all_QC.truncate(before=first_date1, after=last_date1).count().sum()/
      CWS_UrbanClimate_all_QC.truncate(before=first_date1, after=last_date1).size)

print("Number of columns :", len(CWS_UrbanClimate_all_QC.columns))

#Percentage of valid values
print("")
print("Percentage of values AFTER quality criteria", 
      100*CWS_UrbanClimate_all_QC_proc.truncate(before=first_date1, after=last_date1).count().sum()/
      CWS_UrbanClimate_all_QC_proc.truncate(before=first_date1, after=last_date1).size)

print("Number of columns :", len(CWS_UrbanClimate_all_QC_proc.columns))

 
#%%	

###########################################################

# Step 2. COORDINATES - filter - select only stations in QC dataframes with summer values

###########################################################

List_pro = CWS_UrbanClimate_all_QC_proc.columns.values.tolist()
CWS_coordinates_all_QC_proc = CWS_coordinates_all_QC[CWS_coordinates_all_QC['module_final'].isin(List_pro)].reset_index()

CWS_coordinates_all_QC_proc =CWS_coordinates_all_QC_proc.drop(columns=["index","Unnamed: 0"])


#%%	 

###########################################################

# Step 3. Save files

###########################################################

#Directory to save files
#cwd_city_qc_validation = cwd+fr"\data\{city}\3_processed"
os.chdir(cwd_project_proc)

#save weather files
CWS_UrbanClimate_all_QC_proc.to_csv("Temperature_London_2021_CWS_all_QC_G8_proc.csv", index = True , header=True)
CWS_coordinates_all_QC_proc.to_csv("Coordinates_London_2021_CWS_all_QC_G8_proc.csv", index = True , header=True)



#%%	 


######################################################################################################################

#### IDENTIFICATION OF RURAL WEATHER STATIONS FOR TEMPERATURE BASELINE IN SURROUNDING RURAL AREAS

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################


#Directory for city selected
os.chdir(cwd_project_proc)

print("Folder opened: ",cwd_project_proc)


CWS_UrbanClimate_all_QC_proc = pd.read_csv("Temperature_London_2021_CWS_all_QC_G8_proc.csv", index_col='date',parse_dates=True) 
CWS_coordinates_all_QC_proc = pd.read_csv("Coordinates_London_2021_CWS_all_QC_G8_proc.csv") 



#%%	 

###########################################################

# Step 1. Identification of cws for surrounding rural climate (baseline for DeltaT) - two options tested - using data not interpolated

###########################################################


#OPTION 1. Calculation daily min, annual mean of min, and extraction of CWS < 5th percentile
UrbanClimateData2 = CWS_UrbanClimate_all_QC_proc.copy()

UrbanClimateData3 = UrbanClimateData2.resample("d").min()

UrbanClimateData4 = UrbanClimateData3.mean()

UrbanClimateData5 = pd.DataFrame(UrbanClimateData4[(UrbanClimateData4<UrbanClimateData4.quantile(0.05))])

list1 = UrbanClimateData5.index.values.tolist()





#%%	 

#OPTION 2.Calculation daily min and extraction of CWS with minimun values (5th percentile)
UrbanClimateData10 = UrbanClimateData3.copy()

#Calculation of indicators to filter
UrbanClimateData10["Q10"] = np.nan

for i in range(0,len(UrbanClimateData3)):   
    UrbanClimateData10["Q10"].iloc[i] = UrbanClimateData3.iloc[i].quantile(0.05)
    
criteria = UrbanClimateData10[["Q10"]]

UrbanClimateData11 = UrbanClimateData10.copy()

for i in range(0,len(UrbanClimateData11)):   
    UrbanClimateData11.iloc[i] = (UrbanClimateData11.iloc[i]<criteria["Q10"].iloc[i])
    
UrbanClimateData12 = pd.DataFrame(UrbanClimateData11.sum())
UrbanClimateData13 = UrbanClimateData12[(UrbanClimateData12>UrbanClimateData12[0].quantile(0.95))]
UrbanClimateData14 = UrbanClimateData13.dropna()

list2 = UrbanClimateData14.index.values.tolist()


#%%	 


#Get difference between two lists
list3 = list(set(list1)-set(list2))


#%%	 

#DataFrame of lists
list1a = pd.DataFrame({'list1_min_mean': list1})
list2a = pd.DataFrame({'list2_min_frec': list2})
list3a = pd.DataFrame({'list3_diff': list3})

all_lists = pd.concat([list1a, list2a, list3a],axis=1)


#%%	 

###########################################################

# Step 2. Save file with list of rural CWS

###########################################################

#Directory to save files
os.chdir(cwd_project_proc)

#save date
all_lists.to_csv("xtemporal_List_rural_stations.csv", index = True , header=True)



#%%	 

##############################################################################
    
# STEP 3. Baseline temperature - Rural weather statations  - estations with lower anual mean of daily minimum temperature
    
##############################################################################


#Directory for city selected
os.chdir(cwd_project_proc)

print("Folder opened: ",cwd_project_proc)

#list of rural stations
rural_list = pd.read_csv("xtemporal_List_rural_stations.csv")

rural_list1 = rural_list["list1_min_mean"].tolist()
rural_list2 = rural_list["list2_min_frec"].tolist()


#extraction of stations for rural baseline
base_temperature = CWS_UrbanClimate_all_QC_proc[rural_list1]

base_temperature1 = base_temperature.copy()

#mean calculation 
base_temperature1["base_mean"] = np.nan

base_temperature1 = base_temperature1[["base_mean"]]

for i in range(0,len(base_temperature)):   
    base_temperature1["base_mean"].iloc[i] = base_temperature.iloc[i].mean()


base_temperature2 =  base_temperature1.copy()




#%%	 

###########################################################

# Step 4. Save mean rural temperature

###########################################################

#Directory to save files
os.chdir(cwd_project_proc)

#save date
base_temperature2.to_csv("xTemperature_London_2021_CWS_rural_stations.csv", index = True , header=True)



#%%	 

######################################################################################################################

#### ANNUAL ANALISIS   - Cooling degree hours (CDHs, h):  (1) total (2) Daytime (3) Nighttime

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################


#%%	 

###########################################################

# 1.Prepare file 

###########################################################

print(CWS_UrbanClimate_all_QC_proc.info())

#eliminate last datetime value
#cws_data = cws_data.iloc[0:-1]

CWS_UrbanClimate_all_QC_proc = CWS_UrbanClimate_all_QC_proc.truncate(before=first_date, after=last_date)

print(CWS_UrbanClimate_all_QC_proc.info())

#%%	

####################################################

#STEP 1 - CALCULATION OF NIGHT AND DAY HOURS FOR CDHs

#####################################################

def day_night(CWS_UrbanClimate_all_QC_proc,latitude, longitude):
    
    #List of columns
    List_pro = CWS_UrbanClimate_all_QC_proc.columns.values.tolist()
    
    #Helper to calculate day and night periods for CDHs
    column1 = List_pro[0]
    data = CWS_UrbanClimate_all_QC_proc[[column1]]
    
    #lat and long of city
    sun = Sun(latitude, longitude)
    
    data["time_copy"] = data.index

    #datetime to UTC
    data = data.tz_localize('utc')
    data["datetime"] = pd.to_datetime(data.index)
    
    #Calculate of sunrise and sunset
    data["day"] = pd.to_datetime(data["datetime"]).dt.date
    
    #Calculate sunrise and sunset
    data["sunrise"] = np.nan	
    data["sunset"] = np.nan
    
    for i in range(len(data)):
        data["sunrise"].iloc[i] = sun.get_sunrise_time(data["day"].iloc[i])
        data["sunset"].iloc[i] = sun.get_sunset_time(data["day"].iloc[i])
        

    
    #Convert to UTC
    data["sunrise"] = pd.to_datetime(data["sunrise"]).dt.tz_convert("UTC")
    data["sunset"] = pd.to_datetime(data["sunset"]).dt.tz_convert("UTC")

    #data["day"] = pd.to_datetime(data["day"]).dt.tz_localize("UTC")


    print(data.info())

    #CALCUALTE IF NIGHT HOURS == TRUE - TWO OPTIONS: NIGHT (REAL) - NIGTH_PLUS (EXTENDED NIGHT +1 AND +2)
    
    data["night"] = True
    
    for i in range(len(data)):
        if data["datetime"].iloc[i] >=data["sunrise"].iloc[i] and data["datetime"].iloc[i] <=data["sunset"].iloc[i]:
            data["night"].iloc[i] = False
                                         
    
    #data["delta"] = relativedelta(hours=2)
    
    data["night_plus"] = True
    
    for i in range(len(data)):
        if data["datetime"].iloc[i] >=data["sunrise"].iloc[i]+relativedelta(hours=2) and data["datetime"].iloc[i] <=data["sunset"].iloc[i]-relativedelta(hours=1):
            data["night_plus"].iloc[i] = False
    
    return data


#%%	

#Apply function
data_day_night = day_night(CWS_UrbanClimate_all_QC_proc,latitude, longitude)


#%%	

####################################################

#STEP 2 - CALCULATION OF CDHs (total, day, night)

#####################################################

def cdh_calculation(data_day_night,CWS_UrbanClimate_all_QC_proc,CWS_coordinates_all_QC_pro,baseline_t):

    cws_data = CWS_UrbanClimate_all_QC_proc.copy()

    #datetime to UTC
    cws_data = cws_data.tz_localize('utc')
    
    #calculation CDHs
    cws_data = cws_data - baseline_t

    #only positive values (eliminate negatives)
    cws_data = cws_data[(cws_data>0)]

    #convert nan to 0
    cws_data = cws_data.fillna(0) 

    

    #CALCULATION OF CDD
    cdd = cws_data.resample("d").mean().resample("y").sum() #skip nan = false
    cdd["index"] = "CDDs"
    cdd = cdd.reset_index().set_index("index").drop("date",axis=1)

    #CALCULATION OF CDH_NIGHT
    cdh_night = cws_data[(data_day_night["night_plus"]==True)].resample("y").sum()
    cdh_night["index"] = "cdh_night"
    cdh_night = cdh_night.reset_index().set_index("index").drop("date",axis=1)
    
    #CALCULATION OF CDH_DAY
    cdh_day = cws_data[(data_day_night["night_plus"]==False)].resample("y").sum()
    cdh_day["index"] = "cdh_day"
    cdh_day = cdh_day.reset_index().set_index("index").drop("date",axis=1)
    
    #CALCULATION OF CDH_TOTAL
    cdh = cws_data.resample("y").sum()
    cdh["index"] = "cdh_total"
    cdh = cdh.reset_index().set_index("index").drop("date",axis=1)

    #combine results
    new = pd.concat([cdd,cdh,cdh_day,cdh_night],axis=0).T
    
    
    #Add results with CWS ID 
    cws_coordinates = CWS_coordinates_all_QC_proc.copy()
    cws_coordinates["index"] = cws_coordinates["module_final"]
    cws_coordinates = cws_coordinates.set_index("index")

    #cws_coordinates = cws_coordinates.drop('Unnamed: 0',axis=1)

    #combine cws_coordinates with results
    new1 = pd.concat([cws_coordinates,new],axis=1)

    new1 = new1.reset_index().drop('index',axis=1)
    
    return new1



#%%

#Apply function
CWS_coordinates_all_QC_pro_cdh = cdh_calculation(data_day_night,CWS_UrbanClimate_all_QC_proc,CWS_coordinates_all_QC_proc,baseline_t)


#%%

###########################################################

# Step 3. Save files

###########################################################

#Directory to save files
os.chdir(cwd_project_proc)

#save weather files
CWS_coordinates_all_QC_pro_cdh.to_csv("Coordinates_London_2021_CWS_all_QC_G8_proc_CDH.csv", index = True , header=True)



#%%	 



