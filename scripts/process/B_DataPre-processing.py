# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 12:05:20 2021

@author: Jesus Lizana

###########################################################

#INPUT Files: 

###########################################################

#Folder: city/data/1_structured/ 
Coordinates_London_2021_CWS_netatmo         _LCZ
Coordinates_London_2021_CWS_Wunderground    _LCZ
Coordinates_London_2021_OWS_MIDAS           _LCZ

Temperature_London_2021_CWS_Netatmo
Temperature_London_2021_CWS_Wunderground
Temperature_London_2021_OWS_MIDAS


###########################################################

#EXPECTED OUTPUT files:

###########################################################

#Folder: city/data/2_filtered/ - #TARGET: GENERATE 4 FILES
Temperature_London_2021_OWS_QC_I5
Coordinates_London_2021_OWS_QC_I5

Temperature_London_2021_CWS_all_QC_G8
Coordinates_London_2021_CWS_all_QC_G8

#Folder: city/data/reports
 *.csv about statistics before and after QC
 all figures before and after QC


"""
                
#%%	

##### PYTHON LIBRARIES

import os
import sys
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

#statistics
import scipy.stats as stats

#Qn scale estimator proposed by Rousseeuw and Croux as an alternative to the MAD (for modified z-score)
from statsmodels.robust.scale import qn_scale as qn #https://www.statsmodels.org/dev/_modules/statsmodels/robust/scale.html

#t-student distribution and normal distribution
from scipy.stats import t
from scipy.stats import norm 

#FOR DISTANCES BETWEEN COORDINATES
from geopy.distance import geodesic

#In case you want to get rid of the margin in the whole script, you can use
plt.rcParams['axes.xmargin'] = 0   
#plt.rcParams['font.family'] = 'sans-serif'
#plt.rcParams['font.sans-serif'] = 'Tahoma'
#plt.rcParams.update({'font.size': 9})

#Directories
cwd = os.path.dirname(__file__)
os.chdir(cwd)

##### Import OWN LIBRARIES

from functions import qc_functions as qc

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

#colors
color_net = data["color_net"]
color_wund =data["color_wund"]
color_ows =data["color_ows"]
color_cws = data["color_cws"]
color_outliers = data["color_outliers"]


	
#%%	

#Project directories   
cwd_main = cwd[0:-16]
cwd_project = cwd_main+fr"\projectname\{city}"	
cwd_project_raw = cwd_main+fr"\projectname\{city}\data\0_raw"
cwd_project_struct = cwd_main+fr"\projectname\{city}\data\1_structured"
cwd_project_filt = cwd_main+fr"\projectname\{city}\data\2_filtered"
cwd_project_rep = cwd_main+fr"\projectname\{city}\reports"
cwd_project_fig = cwd_main+fr"\projectname\{city}\reports\figures"

#%%	


#QC functions - Instructions

print("QC-I1 ,",qc.QC_I1_datatype.__doc__)

print("QC-I3 ,",qc.QC_I3_limittest.__doc__)
    
print("QC-I4 ,",qc.QC_I4_slopetest.__doc__)
        
print("QC-I5 ,",qc.QC_I5_consistencytest.__doc__)
            
print("QC-G4 ,",qc.QC_G4_duplicate.__doc__)
                
print("QC-G5 ,",qc.QC_G5_distribution.__doc__)
    
print("QC-G6 ,",qc.QC_G6_trust.__doc__)
                        
print("QC-G7 ,",qc.QC_G7_tcorrelation.__doc__)
                            
print("QC-G8 ,",qc.QC_G8_interpolation.__doc__)
    
  
                   
#%%	

######################################################################################################################

#### LOAD FILES 

######################################################################################################################

# go to current location of script
os.chdir(cwd_project_struct)


#### Uploading files

#COORDINATES ##############################

#CWS
CWS_coordinates_net = pd.read_csv(f"Coordinates_{city}_2021_CWS_Netatmo.csv", sep=";")
CWS_coordinates_wund = pd.read_csv(f"Coordinates_{city}_2021_CWS_Wunderground.csv", sep=";")

#OWS
OWS_coordinates = pd.read_csv(f"Coordinates_{city}_2021_OWS_MIDAS.csv", sep=";")



#URBAN CLIMATE ###########################

#Netatmo
CWS_UrbanClimate_net = pd.read_csv(f"Temperature_{city}_2021_CWS_Netatmo.csv", index_col='date',parse_dates=True)  #,dtype=np.float32

#WUNDERGROUND IN REAL TIME ZONE - CONVERT TO UTC
CWS_UrbanClimate_wund = pd.read_csv(f"Temperature_{city}_2021_CWS_Wunderground.csv", index_col='date',parse_dates=True) #,dtype=np.float32

#OWS IN UTC
OWS_Climate = pd.read_csv(f"Temperature_{city}_2021_OWS_MIDAS.csv", index_col='date',parse_dates=True) 


#TAGS ###########################

#Creation of TAGS by CWS and OWS
CWS_coordinates_net["type"] = "CWS - Citizen Weather Stations - Netatmo"
CWS_coordinates_wund["type"] = "CWS - Citizen Weather Stations - Wunderground"
OWS_coordinates["type"] = "OWS - Official Weather Stations" #or Professionally-Operated Weather Stations

print("All files have been correctly charged from : ",cwd_project_struct)



#%%

######################################################################################################################

# INDIVIDUAL QC STEPS

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################


######################################################################################################################

#### QC_I1 - Contaminated data - Data type

######################################################################################################################

#Climate_data
qc.QC_I1_datatype(CWS_UrbanClimate_net)
qc.QC_I1_datatype(CWS_UrbanClimate_wund)
qc.QC_I1_datatype(OWS_Climate)

#Coordinates_data
qc.QC_I1_datatype(CWS_coordinates_net)
qc.QC_I1_datatype(CWS_coordinates_wund)
qc.QC_I1_datatype(OWS_coordinates)


#Detailed info

print(OWS_coordinates.info())
print(OWS_Climate.info())
print("QC_I1 done")

#%%


######################################################################################################################

#### QC_I2	-  Manual visual check	-  Flawed data based on a visual inspection

######################################################################################################################


#FIGURE 1. COMPARISION OF DATA PER DATABASE/SOURCE

before=first_date
after=last_date

fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis
ax.plot(CWS_UrbanClimate_net.iloc[:,0],color=color_net,alpha=0.8,label="CWS - Netatmo",linewidth=1.5)       #.truncate(before, after)
ax.plot(CWS_UrbanClimate_wund.iloc[:,0],color=color_wund,alpha=0.8,label="CWS - Wunderground",linewidth=1.5) #.truncate(before, after)
ax.plot(OWS_Climate.iloc[:,0],color=color_ows,alpha=1,label="Official weather stations",linewidth=1.5)            #.truncate(before, after)
ax.plot(CWS_UrbanClimate_net,color=color_net,alpha=0.4,linewidth=0.6)                                     #.truncate(before, after)
ax.plot(CWS_UrbanClimate_wund,color=color_wund,alpha=0.6,linewidth=0.6)                                    #.truncate(before, after)
ax.plot(OWS_Climate,color=color_ows,alpha=0.8,linewidth=0.6)                                                        #.truncate(before, after)

plt.legend(loc=1)

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="Raw CWS data")

ax.set(ylim=(-20,60))

#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure1.jpg", format='jpg')
plt.show()

print("QC_I2 done")



#%%


######################################################################################################################

#### QC_I3	-  Outliers 1	-  Gross-error limit test	-  Threshold: -40ºC and 60ºC

######################################################################################################################

#Apply function to climate data
CWS_UrbanClimate_net_QC_I3 = qc.QC_I3_limittest(CWS_UrbanClimate_net)
CWS_UrbanClimate_wund_QC_I3 = qc.QC_I3_limittest(CWS_UrbanClimate_wund)
OWS_Climate_QC_I3 = qc.QC_I3_limittest(OWS_Climate)


#Register outliers: 
Outliers_net_I3 = CWS_UrbanClimate_net[(CWS_UrbanClimate_net-CWS_UrbanClimate_net_QC_I3!=0)]
Outliers_wund_I3 = CWS_UrbanClimate_wund[(CWS_UrbanClimate_wund-CWS_UrbanClimate_wund_QC_I3!=0)]
Outliers_OWS_I3 = OWS_Climate[(OWS_Climate-OWS_Climate_QC_I3!=0)]


#Summary of results: 
print("Outlier net: ",Outliers_net_I3.count().sum())
print("Outlier wund: ",Outliers_wund_I3.count().sum())
print("Outlier OWS: ",Outliers_OWS_I3.count().sum())

print("QC_I3 done")

#%%


######################################################################################################################

#### QC_I4	-  Inconsistent data	-  Temporal consistency: slope test -  Threshold: 20ºC/h

######################################################################################################################


#Apply function to climate data
CWS_UrbanClimate_net_QC_I4 = qc.QC_I4_slopetest(CWS_UrbanClimate_net_QC_I3)
CWS_UrbanClimate_wund_QC_I4 = qc.QC_I4_slopetest(CWS_UrbanClimate_wund_QC_I3)
OWS_Climate_QC_I4 = qc.QC_I4_slopetest(OWS_Climate_QC_I3)

#Register outliers: 
Outliers_net_I4 = CWS_UrbanClimate_net_QC_I3[(CWS_UrbanClimate_net_QC_I3-CWS_UrbanClimate_net_QC_I4!=0)]
Outliers_wund_I4 = CWS_UrbanClimate_wund_QC_I3[(CWS_UrbanClimate_wund_QC_I3-CWS_UrbanClimate_wund_QC_I4!=0)]
Outliers_OWS_I4 = OWS_Climate_QC_I3[(OWS_Climate_QC_I3-OWS_Climate_QC_I4!=0)]

#Summary of results: 
print("Outlier net: ",Outliers_net_I4.count().sum())
print("Outlier wund: ",Outliers_wund_I4.count().sum())
print("Outlier OWS: ",Outliers_OWS_I4.count().sum())

print("QC_I4 done")

#%%

######################################################################################################################

#### QC_I5	- Inconsistent data	 -  Temporal consistency: persistence test 	-  Timeframe: 6h

######################################################################################################################

#Apply function to climate data
CWS_UrbanClimate_net_QC_I5 = qc.QC_I5_consistencytest(CWS_UrbanClimate_net_QC_I4)
CWS_UrbanClimate_wund_QC_I5 = qc.QC_I5_consistencytest(CWS_UrbanClimate_wund_QC_I4)
OWS_Climate_QC_I5 = qc.QC_I5_consistencytest(OWS_Climate_QC_I4)

#Register outliers: 
Outliers_net_I5 = CWS_UrbanClimate_net_QC_I4[(CWS_UrbanClimate_net_QC_I4-CWS_UrbanClimate_net_QC_I5!=0)]
Outliers_wund_I5 = CWS_UrbanClimate_wund_QC_I4[(CWS_UrbanClimate_wund_QC_I4-CWS_UrbanClimate_wund_QC_I5!=0)]
Outliers_OWS_I5 = OWS_Climate_QC_I4[(OWS_Climate_QC_I4-OWS_Climate_QC_I5!=0)]

#Summary of results: 
print("Outlier net: ",Outliers_net_I5.count().sum())
print("Outlier wund: ",Outliers_wund_I5.count().sum())
print("Outlier OWS: ",Outliers_OWS_I5.count().sum())

print("QC_I5 done")

#%%


######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################



#%%	
######################################################################################################################

#### FINAL ANALYSIS OF INDIVIDUAL QC STEPS

######################################################################################################################

#Figure 2. Outliers after individual 

Outliers_net = CWS_UrbanClimate_net[(CWS_UrbanClimate_net-CWS_UrbanClimate_net_QC_I5!=0)] #.truncate(before='08-01-2021', after='8-31-2021'
Outliers_wund = CWS_UrbanClimate_wund[(CWS_UrbanClimate_wund-CWS_UrbanClimate_wund_QC_I5!=0)]
Outliers_OWS = OWS_Climate[(OWS_Climate-OWS_Climate_QC_I5!=0)]


#PRINT RESULTS AFTER QC - some outliers were not identified in red - they require more than 1 datetime value. 

fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis

l1 = ax.plot(Outliers_net.iloc[:,0],color=color_outliers,alpha=0.8,label="Outliers",linewidth=1.5)
l2 = ax.plot(CWS_UrbanClimate_net_QC_I5.iloc[:,0],color=color_net,alpha=0.8,label="CWS - Netatmo",linewidth=1.5)
l2 = ax.plot(CWS_UrbanClimate_wund_QC_I5.iloc[:,0],color=color_wund,alpha=0.8,label="CWS - Wunderground",linewidth=1.5)
l3 = ax.plot(OWS_Climate_QC_I5.iloc[:,0],color=color_ows,alpha=1,label="OWS",linewidth=1)

l4 = ax.plot(CWS_UrbanClimate_net_QC_I5,color=color_net,alpha=0.4,label='_Hidden',linewidth=0.6)
l5 = ax.plot(CWS_UrbanClimate_wund_QC_I5,color=color_wund,alpha=0.6,label='_Hidden',linewidth=0.6)
l6 = ax.plot(OWS_Climate_QC_I5,color=color_ows,alpha=0.8,label='_Hidden',linewidth=0.6)
l7 = ax.plot(Outliers_net,color=color_outliers,alpha=1,label='_Hidden',linewidth=1)
l8 = ax.plot(Outliers_wund,color=color_outliers,alpha=1,label='_Hidden',linewidth=1)
l9 = ax.plot(Outliers_OWS,color=color_outliers,alpha=1,label='_Hidden',linewidth=1)


#plt.rcParams['font.family'] = 'sans-serif'
#plt.rcParams['font.sans-serif'] = 'Tahoma'

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="CWS data after individual QC procedures")

ax.set(ylim=(-20,60))

plt.legend(loc=1)


#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure2.jpg", format='jpg')
plt.show() 

                                 
#%%	

### FINAL RESULTS INDIVIDUAL QC STEP: 

print("Outlier CWS - Netatmo: ",Outliers_net.resample("y").count().sum(axis=1).values)
print("Outlier CWS - Wunderground: ",Outliers_wund.resample("y").count().sum(axis=1).values)
print("Outlier OWS: ",Outliers_OWS.resample("y").count().sum(axis=1).values)

print("QC - Individual analysis finished")


#%%	

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################



#%%	

######################################################################################################################

# GROUP QC STEPS

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################



######################################################################################################################

#### QC_G1	- Manual visual check	Flawed data based on a visual inspection	

######################################################################################################################

# FIGURE 3. ALL DATA AFTER QC_I5

fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis
ax.plot(CWS_UrbanClimate_net_QC_I5.iloc[:,0],color=color_net,alpha=0.8,label="CWS - Netatmo",linewidth=1.5)
ax.plot(CWS_UrbanClimate_wund_QC_I5.iloc[:,0],color=color_wund,alpha=0.8,label="CWS - Wunderground",linewidth=1.5)
ax.plot(OWS_Climate_QC_I5.iloc[:,0],color=color_ows,alpha=1,label="Official weather stations",linewidth=1.5)

ax.plot(CWS_UrbanClimate_net_QC_I5,color=color_net,alpha=0.4,linewidth=0.6)
ax.plot(CWS_UrbanClimate_wund_QC_I5,color=color_wund,alpha=0.6,linewidth=0.6) #truncate(before='08-01-2021', after='8-31-2021')
ax.plot(OWS_Climate_QC_I5,color=color_ows,alpha=0.8,linewidth=0.6) #truncate(before='08-01-2021', after='8-31-2021')

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="CWS data after individual QC procedures")

ax.set(ylim=(-20,60))

plt.legend(loc=1)
#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure3.jpg", format='jpg')
plt.show()



#%%

"""
#FIGURE 4. ONE MONTH. COMPARISION OF DATA PER DATABASE/SOURCE - ZOOM

fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis
ax.plot(CWS_UrbanClimate_net_QC_I5.truncate(before='08-01-2021', after='8-31-2021').iloc[:,0],color=color_net,alpha=0.8,label="CWS - Netatmo",linewidth=1.5)
ax.plot(CWS_UrbanClimate_wund_QC_I5.truncate(before='08-01-2021', after='8-31-2021').iloc[:,0],color=color_wund,alpha=0.8,label="CWS - Wunderground",linewidth=1.5)
ax.plot(OWS_Climate_QC_I5.truncate(before='08-01-2021', after='8-31-2021').iloc[:,0],color=color_ows,alpha=1,label="Official weather stations",linewidth=1.5)

ax.plot(CWS_UrbanClimate_net_QC_I5.truncate(before='08-01-2021', after='8-31-2021'),color=color_net,alpha=0.4,linewidth=0.6)
ax.plot(CWS_UrbanClimate_wund_QC_I5.truncate(before='08-01-2021', after='8-31-2021'),color=color_wund,alpha=0.6,linewidth=0.6)
ax.plot(OWS_Climate_QC_I5.truncate(before='08-01-2021', after='8-31-2021'),color=color_ows,alpha=0.8,linewidth=0.6)

plt.legend(loc=1)

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="CWS data after individual QC procedures")

ax.set(ylim=(0, 45))

#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure3b.jpg", format='jpg')
plt.show()

"""

print("QC_G1 done")

#%%


######################################################################################################################

#### QC_G2	- Structural time errors	- Revision and visual check of datetime	UTC Wintertime (UTC + 0:00h) 	

######################################################################################################################

# Figure 5. STRUCTURAL TIME ERROR - UTC 

fig, (ax1, ax2) = plt.subplots(2,1, figsize =(12, 10))
fig.suptitle('VERIFICATION OF STRUCTURAL ERROR - UTC TIME',y=0.94)

# SUPERIOR  ##############################

year1 = datetime.strptime(first_date, '%d-%m-%Y %H:%M').year
#winter day
initial_date1 = f'2-26-{year1}'
final_date1 = f'2-28-{year1}'


ax1.plot(CWS_UrbanClimate_net_QC_I5.truncate(before=initial_date1, after=final_date1).iloc[:,0],color=color_net,alpha=0.8,label="CWS - Netatmo",linewidth=1.5)
ax1.plot(CWS_UrbanClimate_wund_QC_I5.truncate(before=initial_date1, after=final_date1).iloc[:,0],color=color_wund,alpha=0.8,label="CWS - Wunderground",linewidth=1.5)
ax1.plot(OWS_Climate_QC_I5.truncate(before=initial_date1, after=final_date1).iloc[:,0],color=color_ows,alpha=1,label="Official weather stations",linewidth=1.5)

ax1.plot(CWS_UrbanClimate_net_QC_I5.truncate(before=initial_date1, after=final_date1),color=color_net,alpha=0.4,linewidth=0.6)
ax1.plot(CWS_UrbanClimate_wund_QC_I5.truncate(before=initial_date1, after=final_date1),color=color_wund,alpha=0.6,linewidth=0.6)
ax1.plot(OWS_Climate_QC_I5.truncate(before=initial_date1, after=final_date1),color=color_ows,alpha=0.8,linewidth=0.6)

# Set title and labels for axes
ax1.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="Raw CWS data. Winter time")

ax1.set(ylim=(-5, 40))
ax1.legend(loc=1)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax1.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))



##INFERIOR##############################
#summer day
initial_date2 = f'08-2-{year1}'
final_date2 = f'08-4-{year1}'

ax2.plot(CWS_UrbanClimate_net.truncate(before=initial_date2, after=final_date2).iloc[:,0],color=color_net,alpha=0.8,label="CWS - Netatmo",linewidth=1.5)
ax2.plot(CWS_UrbanClimate_wund.truncate(before=initial_date2, after=final_date2).iloc[:,0],color=color_wund,alpha=0.8,label="CWS - Wunderground",linewidth=1.5)
ax2.plot(OWS_Climate.truncate(before=initial_date2, after=final_date2).iloc[:,0],color=color_ows,alpha=1,label="Official weather stations",linewidth=1.5)

ax2.plot(CWS_UrbanClimate_net.truncate(before=initial_date2, after=final_date2),color=color_net,alpha=0.4,linewidth=0.6)
ax2.plot(CWS_UrbanClimate_wund.truncate(before=initial_date2, after=final_date2),color=color_wund,alpha=0.6,linewidth=0.6)
ax2.plot(OWS_Climate.truncate(before=initial_date2, after=final_date2),color=color_ows,alpha=0.8,linewidth=0.6)

# Set title and labels for axes
ax2.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="Raw CWS data. Summer time")

ax2.set(ylim=(5, 40))
ax2.legend(loc=1)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax2.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax2.xaxis.set_major_locator(mdates.DayLocator(interval=5))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure5.jpg", format='jpg')
plt.show()


#%%

#modification of UTC

#DEFINE DATETIME AS LOCAL ZONE (EUROPE/LONDON) AND CONVERT AS UTC (WITHOUT +0:00)
CWS_UrbanClimate2_a = CWS_UrbanClimate_wund_QC_I5.tz_localize('Europe/London', nonexistent='shift_forward',ambiguous=True).tz_convert(None) #"UTC" or None
#CONVERT TO UTC+i (SUM i HOUR WITH DELTATIME)
CWS_UrbanClimate2_b = CWS_UrbanClimate2_a.reset_index()
CWS_UrbanClimate2_b["date"] = CWS_UrbanClimate2_b["date"]+ timedelta(hours=0)
CWS_UrbanClimate2_b = CWS_UrbanClimate2_b.set_index("date").sort_index()
#Eliminate duplicates
CWS_UrbanClimate_wund_QC_G2 = CWS_UrbanClimate2_b.loc[~CWS_UrbanClimate2_b.index.duplicated(keep='first')]

#Elimination of helper variables 
del CWS_UrbanClimate2_a
del CWS_UrbanClimate2_b


#%%


# Figure 6. STRUCTURAL TIME ERROR - UTC 

fig, (ax1, ax2) = plt.subplots(2,1, figsize =(12, 10))
fig.suptitle('VERIFICATION OF STRUCTURAL ERROR - UTC TIME',y=0.94)

# SUPERIOR  ##############################
#Winter day
initial_date1 = f'2-26-{year1}'
final_date1 = f'2-28-{year1}'


ax1.plot(CWS_UrbanClimate_net_QC_I5.truncate(before=initial_date1, after=final_date1).iloc[:,0],color=color_net,alpha=0.8,label="CWS - Netatmo",linewidth=1.5)
ax1.plot(CWS_UrbanClimate_wund_QC_I5.truncate(before=initial_date1, after=final_date1).iloc[:,0],color=color_wund,alpha=0.8,label="CWS - Wunderground",linewidth=1.5)
ax1.plot(OWS_Climate_QC_I5.truncate(before=initial_date1, after=final_date1).iloc[:,0],color=color_ows,alpha=1,label="Official weather stations",linewidth=1.5)
ax1.plot(CWS_UrbanClimate_net_QC_I5.truncate(before=initial_date1, after=final_date1),color=color_net,alpha=0.4,linewidth=0.6)
ax1.plot(CWS_UrbanClimate_wund_QC_G2.truncate(before=initial_date1, after=final_date1),color=color_wund,alpha=0.6,linewidth=0.6)
ax1.plot(OWS_Climate_QC_I5.truncate(before=initial_date1, after=final_date1),color=color_ows,alpha=0.8,linewidth=1.0)

# Set title and labels for axes
ax1.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="Raw CWS data. Winter time")

ax1.set(ylim=(-5, 40))
ax1.legend(loc=1)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax1.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))



##INFERIOR##############################
#summer day
initial_date2 = f'08-2-{year1}'
final_date2 = f'08-4-{year1}'

ax2.plot(CWS_UrbanClimate_net_QC_I5.truncate(before=initial_date2, after=final_date2).iloc[:,0],color=color_net,alpha=0.8,label="CWS - Netatmo",linewidth=1.5)
ax2.plot(CWS_UrbanClimate_wund_QC_I5.truncate(before=initial_date2, after=final_date2).iloc[:,0],color=color_wund,alpha=0.8,label="CWS - Wunderground",linewidth=1.5)
ax2.plot(OWS_Climate_QC_I5.truncate(before=initial_date2, after=final_date2).iloc[:,0],color=color_ows,alpha=1,label="Official weather stations",linewidth=1.5)

ax2.plot(CWS_UrbanClimate_net_QC_I5.truncate(before=initial_date2, after=final_date2),color=color_net,alpha=0.4,linewidth=0.6)
ax2.plot(CWS_UrbanClimate_wund_QC_G2.truncate(before=initial_date2, after=final_date2),color=color_wund,alpha=0.6,linewidth=0.6)
ax2.plot(OWS_Climate_QC_I5.truncate(before=initial_date2, after=final_date2),color=color_ows,alpha=0.8,linewidth=0.6)

# Set title and labels for axes
ax2.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="Raw CWS data. Summer time")

ax2.set(ylim=(5, 40))
ax2.legend(loc=1)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax2.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax2.xaxis.set_major_locator(mdates.DayLocator(interval=5))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure6.jpg", format='jpg')
plt.show()



#%%

#Combination of CWS for combined/group analysis

#Combine CWS data in urban climate
CWS_UrbanClimate_all_QC_G2 = pd.concat([CWS_UrbanClimate_net_QC_I5,CWS_UrbanClimate_wund_QC_G2],axis=1)
CWS_coordinates_all = pd.concat([CWS_coordinates_net,CWS_coordinates_wund],axis=0).reset_index().drop("index",axis=1)

#ELIMINATE CWS not in urbanclimatedata:
List_existingCWS = CWS_UrbanClimate_all_QC_G2.columns.values.tolist()
CWS_coordinates_all = CWS_coordinates_all[CWS_coordinates_all['module_final'].isin(List_existingCWS)] # simbol in python ~ : oposite

print("QC_G2 done - from now, CWSs are combined")

#%%	

######################################################################################################################

#### QC_G3	- Inconsistent data	 - Data units and CWS/OWS id 

######################################################################################################################


# Check manually inconsistent data - Apples; APLES - ºC, lat, long - Explore the following dataframes

print("Check manually inconsistent data")

print(CWS_UrbanClimate_all_QC_G2.info())
print(OWS_Climate_QC_I5.info())
print(CWS_coordinates_all.info())
print(OWS_coordinates.info())

"""

Ready for QC cleaning
GROUP QC STEPS: 
CWS_UrbanClimate_all_QC_I5
OWS_Climate_QC_I5

CWS_coordinates_all
OWS_coordinates


"""

print("QC_G3 done")

#%%	


######################################################################################################################

#### QC_G4	- Duplicate data	Duplicate CWS/OWS

######################################################################################################################

#Apply function to climate data
data_G4,report_G4 = qc.QC_G4_duplicate(CWS_coordinates_all)
  
#%%	

#List of stations "_id" to remove from m1. 
data_G4["list"] = data_G4.module_final[(data_G4["M1"]==True)]

List_G4 = []
List_G4 = list(data_G4["list"].dropna())    


CWS_UrbanClimate_all_QC_G4 = CWS_UrbanClimate_all_QC_G2.drop(List_G4, axis=1)

print("QC_G4 done")


#%%	


######################################################################################################################

#### QC_G5	- Group outliers 2	Statistical analysis: group data distribution	mod_z_score_qn

######################################################################################################################

#Apply function to climate data (ONLY CWS)
weather_Zscore, weather_Zscore_no_outliers, CWS_UrbanClimate_all_QC_G5 = qc.QC_G5_distribution(CWS_UrbanClimate_all_QC_G4,z_score= "mod_z_score_qn", t_distribution=False,low = 0.01, high = 0.95)

#Register outliers: 
Outliers_CWS_G5 = CWS_UrbanClimate_all_QC_G4[(CWS_UrbanClimate_all_QC_G4-CWS_UrbanClimate_all_QC_G5!=0)]

                   
#%%	

#Check statistics 
print(weather_Zscore.describe())

#%%	

#Figure 7. Histogram

initial_date3 = f'08-01-{year1}'
final_date3 = f'08-31-{year1}'

#PRINT HISTORGRAM AFTER QC_G5
num_bins = 10*2*5  # Change this number as you need

fig, ax = plt.subplots()
weather_Zscore.truncate(before=initial_date3 , after=final_date3).iloc[0].hist(bins=num_bins,alpha=0.75,range=[-10, 10],legend=None,color="grey",label="Raw data")
for i in range(1,len(weather_Zscore.truncate(before=initial_date3 , after=final_date3))):
    weather_Zscore.iloc[i].hist(bins=num_bins,alpha=0.2,range=[-8, 8],legend=None,color="grey") #.truncate(before='08-01-2021', after='8-31-2021')

weather_Zscore_no_outliers.truncate(before=initial_date3 , after=final_date3).iloc[0].hist(bins=num_bins,alpha=0.75,range=[-8, 8],legend=None,color=color_cws,label="After step QC_G5")
for i in range(1,len(weather_Zscore_no_outliers.truncate(before=initial_date3 , after=final_date3))):
    weather_Zscore_no_outliers.iloc[i].hist(bins=num_bins,alpha=0.2,range=[-10, 10],legend=None,color=color_cws) #.truncate(before='08-01-2021', after='8-31-2021')
    
plt.legend(loc="upper left")
plt.ylabel("Probability")
plt.xlabel("Data")
plt.title("Histogram")

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure7.jpg", format='jpg')
plt.show()


#%%	


#Figure 8. PRINT RESULTS AFTER QC_G5

Outliers = Outliers_CWS_G5.copy()
CWS_UrbanClimate_all_QC = CWS_UrbanClimate_all_QC_G5.copy() 


fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis
l1 = ax.plot(Outliers.truncate(before=initial_date3, after=final_date3).iloc[:,0],color=color_outliers,alpha=0.8,label="Outliers",linewidth=1.5)

l2 = ax.plot(CWS_UrbanClimate_all_QC.truncate(before=initial_date3, after=final_date3),color=color_cws,alpha=0.6,label='_Hidden',linewidth=0.6)
#l3 = ax.plot(OWS_Climate_QC_I5.truncate(before='08-01-2021', after='8-31-2021'),color=color_ows,alpha=0.6,label='_Hidden',linewidth=0.6)
l4 = ax.plot(Outliers.truncate(before=initial_date3, after=final_date3),color=color_outliers,alpha=0.6,label='_Hidden',linewidth=0.6)

#plt.rcParams['font.family'] = 'sans-serif'
#plt.rcParams['font.sans-serif'] = 'Tahoma'

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="CWS data after QC_G5")

ax.set(ylim=(5, 45))

plt.legend()


#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure8.jpg", format='jpg')
plt.show()



print("QC_G5 done")


#%%	


######################################################################################################################

#### QC_G6	- Group outliers 4	Statistical analysis: constant errors	Threshold: Outliers > 25%

######################################################################################################################

#Apply function to climate data (ONLY CWS)
CWS_UrbanClimate_all_QC_G6 = qc.QC_G6_trust(CWS_UrbanClimate_all_QC_G5,Outliers,cutOff=0.75,time="M")

#Register outliers: 
Outliers_CWS_G6 = CWS_UrbanClimate_all_QC_G5[(CWS_UrbanClimate_all_QC_G5-CWS_UrbanClimate_all_QC_G6!=0)]

#%%	

#Figure 9. PRINT RESULTS AFTER QC_G6

Outliers = Outliers_CWS_G6.copy()
CWS_UrbanClimate_all_QC = CWS_UrbanClimate_all_QC_G6.copy() 

	
fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis
l1 = ax.plot(Outliers.truncate(before=initial_date3, after=final_date3).iloc[:,0],color=color_outliers,alpha=0.8,label="Outliers",linewidth=1.5)

l2 = ax.plot(CWS_UrbanClimate_all_QC.truncate(before=initial_date3, after=final_date3),color=color_cws,alpha=0.6,label='_Hidden',linewidth=0.6)
l3 = ax.plot(Outliers.truncate(before=initial_date3, after=final_date3),color=color_outliers,alpha=0.6,label='_Hidden',linewidth=0.6)

#plt.rcParams['font.family'] = 'sans-serif'
#plt.rcParams['font.sans-serif'] = 'Tahoma'

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="CWS data after QC_G6")

ax.set(ylim=(5, 45))

plt.legend()


#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure9.jpg", format='jpg')
plt.show()


print("QC_G6 done")

#%%	


######################################################################################################################

#### QC_G7	- Group outliers 3	Statistical analysis: group temporal correlation	Threshold: Pearson correlation coefficient <0.9

######################################################################################################################


#Apply function to climate data (ONLY CWS)
CWS_UrbanClimate_all_QC_G7 = qc.QC_G7_tcorrelation(CWS_UrbanClimate_all_QC_G6,cutOff=0.9).sort_index()

#Register outliers: 
Outliers_CWS_G7 = CWS_UrbanClimate_all_QC_G6[(CWS_UrbanClimate_all_QC_G6-CWS_UrbanClimate_all_QC_G7!=0)]

#%%	

#Figure 10. PRINT RESULTS AFTER QC_G7

Outliers = Outliers_CWS_G7.copy()
CWS_UrbanClimate_all_QC = CWS_UrbanClimate_all_QC_G7.copy()

fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis
l1 = ax.plot(Outliers.truncate(before=initial_date3, after=final_date3).iloc[:,0],color=color_outliers,alpha=0.8,label="Outliers",linewidth=1.5)

l2 = ax.plot(CWS_UrbanClimate_all_QC.truncate(before=initial_date3, after=final_date3),color=color_cws,alpha=0.6,label='_Hidden',linewidth=0.6)
l3 = ax.plot(Outliers.truncate(before=initial_date3, after=final_date3),color=color_outliers,alpha=0.6,label='_Hidden',linewidth=0.6)

#plt.rcParams['font.family'] = 'sans-serif'
#plt.rcParams['font.sans-serif'] = 'Tahoma'

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="CWS data after QC_G7")

ax.set(ylim=(5, 45))

plt.legend()


#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure10.jpg", format='jpg')
plt.show()






print("QC_G7 done")


#%%	


######################################################################################################################

#### QC_G8	- Missing data	Filling gap 	 	

######################################################################################################################

CWS_UrbanClimate_all_QC_G8 = qc.QC_G8_interpolation(CWS_UrbanClimate_all_QC_G7,2)


#END OF QUALITY CONTROL PROCEDURES 
print("QC_G8 done - End of group QC steps")


#%%	


######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################



#%%	

######################################################################################################################

#### FINAL ANALYSIS OF GROUP QC STEPS

######################################################################################################################

#Figure 11. Outliers after group analysis 

Outliers_G = CWS_UrbanClimate_all_QC_G2[(CWS_UrbanClimate_all_QC_G2-CWS_UrbanClimate_all_QC_G8!=0)]

#PRINT RESULTS AFTER QC_group

Outliers = Outliers_G.copy()
CWS_UrbanClimate_all_QC = CWS_UrbanClimate_all_QC_G8.copy()
OWS_Climate_QC = OWS_Climate_QC_I5.copy()

fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis
l1 = ax.plot(Outliers.iloc[:,0],color=color_outliers,alpha=0.8,label="Outliers",linewidth=1.5)
l2 = ax.plot(CWS_UrbanClimate_all_QC.iloc[:,0],color=color_cws,alpha=0.8,label="CWS",linewidth=1.5)
l3 = ax.plot(OWS_Climate_QC.iloc[:,0],color=color_ows,alpha=1,label="OWS",linewidth=1.5)

l6 = ax.plot(Outliers,color=color_outliers,alpha=0.4,label='_Hidden',linewidth=0.6)
l4 = ax.plot(CWS_UrbanClimate_all_QC,color=color_cws,alpha=0.6,label='_Hidden',linewidth=0.6)
l5 = ax.plot(OWS_Climate_QC,color=color_ows,alpha=0.8,label='_Hidden',linewidth=0.6)

#plt.rcParams['font.family'] = 'sans-serif'
#plt.rcParams['font.sans-serif'] = 'Tahoma'

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="CWS data after group QC procedures")

ax.set(ylim=(-20,60))

plt.legend(loc=1)


#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure11.jpg", format='jpg')
plt.show()



#%%	

#Figure 12. Final data after group analysis 

Outliers_G = CWS_UrbanClimate_all_QC_G2[(CWS_UrbanClimate_all_QC_G2-CWS_UrbanClimate_all_QC_G8!=0)]

#PRINT RESULTS AFTER QC_group

Outliers = Outliers_G.copy()
CWS_UrbanClimate_all_QC = CWS_UrbanClimate_all_QC_G8.copy()
OWS_Climate_QC = OWS_Climate_QC_I5.copy()

fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis
#l1 = ax.plot(Outliers.iloc[:,0],color=color_outliers,alpha=0.8,label="Outliers",linewidth=1.5)
l2 = ax.plot(CWS_UrbanClimate_all_QC.iloc[:,0],color=color_cws,alpha=0.8,label="CWS",linewidth=1.5)
l3 = ax.plot(OWS_Climate_QC.iloc[:,0],color=color_ows,alpha=1,label="OWS",linewidth=1.5)

#l6 = ax.plot(Outliers,color=color_outliers,alpha=0.4,label='_Hidden',linewidth=0.6)
l4 = ax.plot(CWS_UrbanClimate_all_QC,color=color_cws,alpha=0.6,label='_Hidden',linewidth=0.6)
l5 = ax.plot(OWS_Climate_QC,color=color_ows,alpha=0.8,label='_Hidden',linewidth=0.6)

#plt.rcParams['font.family'] = 'sans-serif'
#plt.rcParams['font.sans-serif'] = 'Tahoma'

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="CWS data after group QC procedures")

ax.set(ylim=(-20,60))

plt.legend(loc=1)


#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure12.jpg", format='jpg')
plt.show()


#%%	

"""

#Figure 13. PRINT RESULTS AFTER QC_group - ZOOM


fig, ax = plt.subplots(figsize=(14, 3))

# Add x-axis and y-axis
l1 = ax.plot(Outliers.truncate(before='08-01-2021', after='8-7-2021').iloc[:,0],color=color_outliers,alpha=0.8,label="Outliers",linewidth=1.5)

l2 = ax.plot(CWS_UrbanClimate_all_QC.truncate(before='08-01-2021', after='8-7-2021'),color=color_cws,alpha=0.8,label='_Hidden',linewidth=0.6)
l3 = ax.plot(Outliers.truncate(before='08-01-2021', after='8-7-2021'),color=color_outliers,alpha=0.3,label='_Hidden',linewidth=0.6)

#plt.rcParams['font.family'] = 'sans-serif'
#plt.rcParams['font.sans-serif'] = 'Tahoma'

# Set title and labels for axes
ax.set(xlabel="Time",
       ylabel="Temperature (ºC)",
       title="CWS data after group QC procedures")

ax.set(ylim=(5, 45))

plt.legend()


#margins - 0 applied to all script 
#plt.margins(x=0)

# Define the date format
date_form = DateFormatter("%y-%m-%d")
ax.xaxis.set_major_formatter(date_form)

# Ensure a major tick for each week using (interval=1) 
#ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))

os.chdir(cwd_project_fig)
plt.savefig(f"02_Pre-processing_{city}_figure12b.jpg", format='jpg')
plt.show()

"""

#%%	

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################

#%%	


######################################################################################################################

# FINAL ANALYSIS - statistics

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################


#Analysis of data per QC step - CWS
size1=[CWS_UrbanClimate_net.size+CWS_UrbanClimate_wund.size,
       CWS_UrbanClimate_net_QC_I3.size+CWS_UrbanClimate_wund_QC_I3.size,
       CWS_UrbanClimate_net_QC_I4.size+CWS_UrbanClimate_wund_QC_I4.size,
       CWS_UrbanClimate_net_QC_I5.size+CWS_UrbanClimate_wund_QC_I5.size,
       CWS_UrbanClimate_all_QC_G4.size,
       CWS_UrbanClimate_all_QC_G5.size,
       CWS_UrbanClimate_all_QC_G6.size,
       CWS_UrbanClimate_all_QC_G7.size,
       CWS_UrbanClimate_all_QC_G8.size]


#%%	

number1=[CWS_UrbanClimate_net.stack().count()+CWS_UrbanClimate_wund.stack().count(),
         CWS_UrbanClimate_net_QC_I3.stack().count()+CWS_UrbanClimate_wund_QC_I3.stack().count(),
         CWS_UrbanClimate_net_QC_I4.stack().count()+CWS_UrbanClimate_wund_QC_I4.stack().count(),
         CWS_UrbanClimate_net_QC_I5.stack().count()+CWS_UrbanClimate_wund_QC_I5.stack().count(),
         CWS_UrbanClimate_all_QC_G4.stack().count(),
         CWS_UrbanClimate_all_QC_G5.stack().count(),
         CWS_UrbanClimate_all_QC_G6.stack().count(),
         CWS_UrbanClimate_all_QC_G7.stack().count(),
         CWS_UrbanClimate_all_QC_G8.stack().count()]

#%%	
percentage0= [(i / j)*100 for i, j in zip( number1,size1)]

#%%	
number_CWS = [len(CWS_UrbanClimate_net.columns)+len(CWS_UrbanClimate_wund.columns),
              len(CWS_UrbanClimate_net_QC_I3.columns)+len(CWS_UrbanClimate_wund_QC_I3.columns),
              len(CWS_UrbanClimate_net_QC_I4.columns)+len(CWS_UrbanClimate_wund_QC_I4.columns),
              len(CWS_UrbanClimate_net_QC_I5.columns)+len(CWS_UrbanClimate_wund_QC_I5.columns),
              len(CWS_UrbanClimate_all_QC_G4.columns),
              len(CWS_UrbanClimate_all_QC_G5.columns),
              len(CWS_UrbanClimate_all_QC_G6.columns),
              len(CWS_UrbanClimate_all_QC_G7.columns),
              len(CWS_UrbanClimate_all_QC_G8.columns)]


#%%	
#Outliers
helper1 = [CWS_UrbanClimate_net.stack().count()+CWS_UrbanClimate_wund.stack().count(),
           CWS_UrbanClimate_net.stack().count()+CWS_UrbanClimate_wund.stack().count(),
           CWS_UrbanClimate_net_QC_I3.stack().count()+CWS_UrbanClimate_wund_QC_I3.stack().count(),
           CWS_UrbanClimate_net_QC_I4.stack().count()+CWS_UrbanClimate_wund_QC_I4.stack().count(),
           CWS_UrbanClimate_net_QC_I5.stack().count()+CWS_UrbanClimate_wund_QC_I5.stack().count(),
           CWS_UrbanClimate_all_QC_G4.stack().count(),
           CWS_UrbanClimate_all_QC_G5.stack().count(),
           CWS_UrbanClimate_all_QC_G6.stack().count(),
           CWS_UrbanClimate_all_QC_G7.stack().count()]

percentage1 = [(i / j -1)*100 for i, j in zip(number1,helper1)]

percentage2 = (number1/(CWS_UrbanClimate_net.stack().count()+CWS_UrbanClimate_wund.stack().count())-1)*100
percentage2 = percentage2.tolist()

#%%	

#statistics 
statistics_QC = {'QC level': ["raw","QC_I3","QC_I4","QC_I5","QC_G4","QC_G5","QC_G6","QC_G7","QC_G8"],
                 'Size of DataFrame': size1, 
                 'Number of available data': number1, 
                 'Available data (%)': percentage0, 
                 'Number of available CWS': number_CWS, 
                 'Outliers identified (%)': percentage1,
                 "Accumulated outliers (%)": percentage2
                 }

df_statistics_QC = pd.DataFrame(data=statistics_QC)


#%%	

print(OWS_Climate_QC_I5.size)
print(OWS_Climate_QC_I5.stack().count()/OWS_Climate_QC_I5.size)
print((OWS_Climate_QC_I5.stack().count()/OWS_Climate_QC_I4.stack().count()-1)*100)

#%%	


#Analysis of data per QC step - OWS
size1=[OWS_Climate.size,
       OWS_Climate_QC_I3.size,
       OWS_Climate_QC_I4.size,
       OWS_Climate_QC_I5.size]

number1=[OWS_Climate.stack().count(),
         OWS_Climate_QC_I3.stack().count(),
         OWS_Climate_QC_I4.stack().count(),
         OWS_Climate_QC_I5.stack().count()]

percentage0= [(i / j)*100 for i, j in zip(number1,size1)]

number_CWS = [len(OWS_Climate_QC.columns),
              len(OWS_Climate_QC_I3.columns),
              len(OWS_Climate_QC_I4.columns),
              len(OWS_Climate_QC_I5.columns)]

#Outliers
helper1 = [OWS_Climate.stack().count(),
           OWS_Climate.stack().count(),
           OWS_Climate_QC_I3.stack().count(),
           OWS_Climate_QC_I4.stack().count()]

percentage1 = [(i / j -1)*100 for i, j in zip(number1,helper1)]
percentage2 = (number1/OWS_Climate.stack().count()-1)*100

#statistics 
statistics_QC_OWS = {'QC level': ["raw","QC_I3","QC_I4","QC_I5"],
                 'Size of DataFrame': size1, 
                 'Number of available data': number1, 
                 'Available data (%)': percentage0, 
                 'Number of available CWS': number_CWS, 
                 'Outliers identified (%)': percentage1,
                 "Accumulated outliers (%)": percentage2
                 }

df_statistics_QC_OWS = pd.DataFrame(data=statistics_QC_OWS)

#%%	

#Update coordinates files and save
List_helper = list(CWS_UrbanClimate_all_QC_G8.columns.values)

CWS_coordinates_all_QC = CWS_coordinates_all[CWS_coordinates_all['module_final'].isin(List_helper)]

#%%	


#Directory to save files
os.chdir(cwd_project_rep)

#save statistics
df_statistics_QC.to_csv(f"Pre-processing_{city}_{year1}_CWS_all_G8_g8_Statistics.csv", index = True , header=True)
df_statistics_QC_OWS.to_csv(f"Pre-processing_{city}_{year1}_OWS_all_G8_g8_Statistics.csv", index = True , header=True)


#Directory to save filtered files after cleaning and quality control
os.chdir(cwd_project_filt)

CWS_UrbanClimate_all_QC_G8.to_csv(f"Temperature_{city}_2021_CWS_all_QC_G8.csv", index = True , header=True)
CWS_coordinates_all_QC.to_csv(f"Coordinates_{city}_2021_CWS_all_QC_G8.csv", index = True , header=True)


OWS_Climate_QC_I5.to_csv(f"Temperature_{city}_2021_OWS_QC_I5.csv", index = True , header=True)
OWS_coordinates.to_csv(f"Coordinates_{city}_2021_OWS_QC_I5.csv", index = True , header=True)

print("")
print("Pre-processing completed successfully")

#%%	

