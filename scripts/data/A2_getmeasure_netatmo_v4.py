# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 11:32:28 2021

@author: Jesus Lizana

Extraction of CWS measures from netatmo

###########################################################

#INPUT Files: 

###########################################################

projectdata.json (inputs required for extraction)

###########################################################

#EXPECTED OUTPUT files:

###########################################################

#Folder: data/0_raw

"""
	
#%%	

import os
import sys

import requests
import pandas as pd
import glob
import datetime
import numpy as np
import json

#to sum relative datatime
from dateutil.relativedelta import relativedelta
import time
from time import sleep

import winsound

#Directories
cwd = os.path.dirname(__file__)
os.chdir(cwd)

#%%	

#read json file - input data for extraction
with open('projectdata.json', 'r') as fp:
    data = json.load(fp)
  
#%%	   
 
###########################################################

# INPUT DATA required to select city - Import from project config.py manually 

###########################################################

city = data["city"]
lat = data["lat"]
long = data["long"]
plot =  data["plot"]
dist = plot/2 
subplots= data["grid"] #GRID SIZE FOR DATA EXTRACTION FROM 1 TO 0.02

#token
#"Bearer 60e70ef3d3b12959ea6a382f|18cdb20f595d6c9259f2d6b911e2fed2" 
#https://dev.netatmo.com/apidocumentation/weather#getpublicdata
auth1= data["auth1"]

	
#%%	

#Project directories   
cwd_main = cwd[0:-13]
cwd_project = cwd_main+fr"\projectname\{city}"	
cwd_project_raw = cwd_main+fr"\projectname\{city}\data\0_raw"
cwd_project_raw_temp = cwd_main+fr"\projectname\{city}\data\0_raw\temp"
	
#%%	

##############################################################################
				
# DOWNLOAD STATIONS FROM NETATMO

##############################################################################

#STEP 1. UPLOAD ID of stations
#------------------------------------------------------------------------------

os.chdir(cwd_project_raw)

# Import file with CLEANING STATIONS IN THE AREA
db_stations6 = pd.read_csv(f"Coordinates_{city}_CWS_Netatmo.csv") 
#print ("See initial file details")
#print (db_stations6.info())



#%%

#STEP 2. Functions to extract data using Netatmo API
#------------------------------------------------------------------------------

def epoch(date):
    date_sal=datetime.datetime.fromtimestamp(date)
    return date_sal

def media(lista):
    return np.mean(lista)

#parameter can be "temperature" or "humidity"
def download_estation(_id,mod,begin,end,auth,parameter):
    _id=_id.replace(":","%3A")
    mod1=mod.replace(":","%3A")
    URL=f'https://api.netatmo.com/api/getmeasure?device_id={_id}&module_id={mod1}&scale=1hour&type={parameter}&date_begin={begin}&date_end={end}&optimize=false&real_time=false'
    #auth="Bearer 60e70ef3d3b12959ea6a382f|381513ccf09eaa0f6543086cb09ef722"  #ACTUALIZAR TOKEN
  
    res=requests.get(URL)
    payload={"accept": "application/json","Authorization":auth}

    res=requests.get(URL, headers=payload)
    res=res.json()
    
    
    try:
        data=pd.json_normalize(res['body'])

        data=data.transpose()
        data=data.reset_index()
        data=data.rename(columns={'index':'date',0:mod})
    
        data['date']=data['date'].astype('int')
        data['date']=data['date'].apply(epoch)
        data['date']=pd.to_datetime(data.date, format='%Y-%m-%d %H:%M:%S', dayfirst=True)
        #data['date']=data['date']+datetime.timedelta(hours=2)
    
        data[mod]=data[mod].apply(media)
        data=data.set_index('date')
        data=data.resample('h').mean()
        return data
        
    except:
        print(mod,"An error occurred")
    


#%%

#STEP 3. Period to extract data
#------------------------------------------------------------------------------

#Introduce period to extract data (1 month is 744 values, MAX per request 1024)
#https://www.epochconverter.com/

date_begin0 = datetime.datetime.strptime(data["first_date"], '%d-%m-%Y %H:%M') 
date_end0 = datetime.datetime.strptime(data["last_date"], '%d-%m-%Y %H:%M') 

#date_begin = datetime.datetime(2021, 1, 1, 0, 0)
#date_end = datetime.datetime(2021, 12, 31, 23, 0)



#%%

#STEP 4. Check duplicates
#------------------------------------------------------------------------------

        
"Test to check duplicate stations"
db_stations7 = db_stations6[["module_final"]]
#db_stations7 = db_stations7.drop_duplicates()

Duplicate = db_stations7[db_stations7.duplicated()]

if len(Duplicate)==0:
    print("No duplicate stations in list")
    print("Total number of stations to extract: ",len(db_stations6))
else: 
    print("Duplicate stations found :",len(Duplicate),"/",len(db_stations6))
    print("Check duplicate stations",Duplicate["module_final"].unique())



#%%

#STEP 4. Extraction
#------------------------------------------------------------------------------

#Go to new temporal directory
os.chdir(cwd_project_raw_temp)

"""
Steps: 
    1.Verify if file has been already donwloaded. If yes, pass
    2.If not, download file. If empty, pass (empty +1); if data, save in folder. 
    3.If empty>10, exit (to stop during long unconnected period) 
    4. Elimnate last files, check token and conection, start again
    
"""


emptyfile=0
number=0
for i in range(0,len(db_stations6)):
    station1 = pd.DataFrame()
    _id = db_stations6.loc[i,"_id"]
    mod = db_stations6.loc[i,"module_final"]
    
    #Identification if station has been already downloaded: 
    _id1=_id.replace(":",".")
    mod2=mod.replace(":",".")
    stationname = f'{_id1}_{mod2}.csv'   #modified - previous with number: f'{i}_{_id1}_{mod2}.csv'
    
    my_file= "/"+ stationname
    cwd2 = cwd_project_raw_temp + my_file
    
    number=number+1 #conteo de estations
    
    if os.path.exists(cwd2) is True:
        print(i,mod,"already downloaded")
    
    else: 
        print(i,mod,"doesn't exist, extracting...")
        date_begin = date_begin0
        date_end = date_end0
        
        while(date_begin < date_end):
            date_end1 = date_begin + relativedelta(months=1)
         
            date_begin_int = int(date_begin.timestamp())
            date_end_int = int(date_end1.timestamp())
   
            df = download_estation(_id,mod,date_begin_int,date_end_int,auth1,parameter="temperature") #parameter: temperature or humidity

            station1 = pd.concat([station1,df])
            station1 = station1[~station1.index.duplicated(keep='first')]
        
            print(mod,number, i," of ",len(db_stations6),"--",date_begin.year,"/",date_begin.month)
        
            date_begin = date_end1
            time.sleep(1)  
        
        
        if len(station1)>0:
            #SAVE CSV FILE in city folder
            station1.to_csv(stationname, index = True , header=True)
    
            time.sleep(6)    
            #urbanclimatedata = pd.concat([urbanclimatedata,station1],axis=1)
            print(mod, "Done!",number," of ",len(db_stations6),"- Empty files: ",emptyfile)
        else:
            emptyfile=emptyfile+1
            print(mod,"Empty file","Total",emptyfile)
        
    if emptyfile>10:
        frequency = 1500  # Set Frequency To 2500 Hertz
        duration = 500  # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)
        
        sys.exit("Error!, Number of empty files>10: ",emptyfile)
        
print("Total empty files",emptyfile)


#%%

#STEP 5. Combination of files into one single csv file
#------------------------------------------------------------------------------

urbanclimatedata = pd.DataFrame()
cwd3 = cwd_project_raw_temp +"\*.csv"

number = 0
for f in glob.glob(cwd3):
    number = number+1
    print("Total number of stations extracted: ",len(number))
    appenddata = pd.read_csv(f,parse_dates=True, index_col='date')
    urbanclimatedata = pd.concat([urbanclimatedata,appenddata],axis=1)

#eliminate columns duplicated
urbanclimatedata1 = urbanclimatedata.loc[:,~urbanclimatedata.columns.duplicated()]


#%%

# Directory to save file
os.chdir(cwd_project_raw)

name = f'Temperature_{city}_{date_begin0.year}_CWS_Netatmo.csv'

#SAVE CSV FILE WITH ALL URBAN WEATHER FILES IN THE AREA
urbanclimatedata1.to_csv(name, index = True , header=True)
print("New file has been created: ",name)
print(f"It has been saved in folder: ", cwd_project_raw)
print("List of files in folder")
print(os.listdir()) #check if file has been saved


#%%

























