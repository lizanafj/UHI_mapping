# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 11:32:28 2021

@author: Jesus Lizana

Extraction of CWS location and ID from netatmo

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

#import sys
import os
import requests
import pandas as pd
import numpy as np
import json

#geodata
import geopy
from geopy import distance
from geopy.distance import geodesic

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
	
#%%	

#Extension (area for extraction)
center_pt = [lat,long]

#calculation of zoom in coordenadas
# given: lat1, lon1, b = bearing in degrees, d = distance in kilometers
origin = geopy.Point(center_pt)

#lat
a = distance.distance(kilometers=dist).destination(origin,0) #lat
lat_d = repr(a[0])
lat_d = float(lat_d) - float(lat)

#long
b = distance.distance(kilometers=dist).destination(origin,90) #lat
lon_d = repr(b[1])
lon_d = float(lon_d) - float(long)
 
#Definition of extent - frame for mapping
extent = [center_pt[1]-lon_d,center_pt[1]+lon_d,center_pt[0]-lat_d,center_pt[0]+lat_d] # adjust to zoom  
print("Extent: ",extent)



#%%	

##############################################################################
				
# DOWNLOAD STATIONS FROM NETATMO

##############################################################################

#STEP 1. Inputs for data extraction

#Frame for data extraction
base_lat_ne = extent[3]
base_lon_ne =  extent[1]
base_lat_sw =  extent[2]
base_lon_sw =  extent[0]



# calc each subextent size
lon_step = subplots 
lat_step = subplots 

db_stations2 = pd.DataFrame(columns=["_id","modules","place.location"]) #,"place.city"

#STEP 2. Loop for data extraction per grid size
currentStep=0 #lanzar por debajo de este si se para

# we cut the extent in x/x and go through each sub-extent
lat_sw = base_lat_sw
lon_sw = base_lon_sw
while(lat_sw < base_lat_ne):
    lat_ne = lat_sw + lat_step
    
    while(lon_sw < base_lon_ne):
        lon_ne = lon_sw + lon_step
        
        URL2 =f'https://api.netatmo.com/api/getpublicdata?lat_ne={lat_ne}&lon_ne={lon_ne}&lat_sw={lat_sw}&lon_sw={lon_sw}&filter=false'
        payload={"accept": "application/json","Authorization":auth1}
        res=requests.get(URL2, headers=payload)
        res=res.json()

        df=pd.json_normalize(res['body'])
        #df=df[["_id","modules","place.location","place.city"]]  #da error cuando no hay estaciones.
        
        db_stations2 = pd.concat([db_stations2,df])
        db_stations2=db_stations2[["_id","modules","place.location"]] #,"place.city"
        

        currentStep=currentStep+1
        print("cuadrante",currentStep,lat_sw,lon_sw,lat_ne,lon_ne,len(df),len(db_stations2))
        lon_sw = lon_ne
    lon_sw=base_lon_sw
    lat_sw=lat_ne

print("")    
print(f"Number of stations: {len(db_stations2)}","- Grid size for extraction: ",lat_step)  
    
#Reset index again (ordering)
db_stations3 = db_stations2.copy().reset_index(drop=True).astype(str) #convertimos en str todo para depurar luego el contenido. 


#STEP 3. Check for duplicate data

duplicated = db_stations3.duplicated().sum() #True get converted to 1 and False get converted to 0
print("")
print("Duplicated :",duplicated)

finalstations = (~db_stations3.duplicated()).sum() #to count the number of non-duplicates (The number of False)
print("Final number of stations :",finalstations)


# Extract duplicate rows
db_stations4 = db_stations3.drop_duplicates()

db_stations4 = db_stations4.reset_index(drop=True)

#Renombrar
db_stations4 = db_stations4.rename(columns={"place.location": "coordinates"})

#CONVERTIR COLUMNAS EN STR PARA DIVIDIR DATOS
db_stations4['modules']= db_stations4.modules.apply(str)
db_stations4['coordinates']=db_stations4.coordinates.apply(str)

#FUNCION PARA ELIMINAR SIGNOS Y DEJAR SOLO ESPACIO
def eliminar_corchete(data):
    data=data.replace("[","")
    data=data.replace("]","")
    data=data.replace(",","")
    data=data.replace(',',"")
    data=data.replace("'","")
    return data

#Aplicamos funcion
db_stations4['modules']=db_stations4['modules'].apply(eliminar_corchete)
db_stations4['coordinates']=db_stations4['coordinates'].apply(eliminar_corchete)

#helper in case of empty file
#helper = db_stations4.iloc[43:44,:]
#db_stations4 = pd.concat([db_stations4,helper]).reset_index(drop=True)


#split columns
modules=db_stations4['modules'].str.split(expand=True)

modules.columns=['mod1','mod2','mod3']

coordinates=db_stations4['coordinates'].str.split(expand=True)
coordinates.columns=['long','lat']

#Crear lista con true or false de coincidencia con 02 sensor (mascara según Elisa)
modules["mod_01"] = (modules['mod1'].str.slice(0, 2)=="02")
modules["mod_02"] = (modules['mod2'].str.slice(0, 2)=="02")
modules["mod_03"] = (modules['mod3'].str.slice(0, 2)=="02")

#Bucle para coger datos cuando exista coincidencia con sensor 02 - SENSOR EXTERIOR: 
list_true = ['mod_01','mod_02','mod_03']

for i in list_true:
    for n in range(0,len(modules)):
        if modules.loc[n,i]==True and i=="mod_01":
            modules.loc[n,"module_final"] = modules.loc[n,"mod1"]
        elif modules.loc[n,i]==True and i=="mod_02":
            modules.loc[n,"module_final"] = modules.loc[n,"mod2"]
        elif modules.loc[n,i]==True and i=="mod_03":
            modules.loc[n,"module_final"] = modules.loc[n,"mod3"]
         
           
            
#STEP 4. SELECTION ONLY OF REQUIRED DATA - FINAL DATAFRAME
#------------------------------------------------------------------------------
db_stations5 = pd.concat([db_stations4["_id"],modules["module_final"],coordinates],axis=1)

#if helper
#db_stations5 = db_stations5[:-1]

print("")
print ("Example of final file extracted")
print (db_stations5.head())

print("Final number of stations :",len(db_stations5))
      

#SAVE CSV FILE WITH CLEANING STATIONS IN THE AREA
os.chdir(cwd_project_raw)

db_stations5.to_csv(f"Coordinates_{city}_CWS_Netatmo.csv", index = False , header=True)
print(f"File has been saved in folder: {cwd}")
print(os.listdir()) #check if file has been saved

















