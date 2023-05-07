# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 12:05:20 2021

@author: Jesus Lizana

"""

import os

#geodata
import geopy
from geopy import distance
                       
#%%	
###########################################################

#INPUT DATA required to select city

###########################################################

city = "Seville"

#location and extent
lat = 37.389915605750744
long = -5.974931508614992
plot =  25 # to define the grid size to map in km (kmxkm), e.g. 70 = 70x70km2


#timeframe for data extraction -- day-month-year
first_date='01-01-2022 00:00'  
last_date='31-12-2022 23:00'

#Timeframe criteria to eliminate statations with data availability <90%  -- day-month-year
first_date1='20-05-2022'  
last_date1='20-09-2022'

#colors
color_net = 'lightskyblue' 
color_wund ="royalblue" 
color_ows ='k'
color_cws = 'blue'
color_outliers = 'r'


                       
#%%	

###########################################################

#INTERNAL VARIABLES - automatically calculated - don't modify

###########################################################

#Directories
cwd_project = os.path.dirname(__file__)

char = len(city)+13
cwd_main = cwd_project[:-char]

cwd_project = cwd_main + f"\projectname\{city}"
cwd_scripts_data = cwd_main + r"\scripts\data"
cwd_scripts_process = cwd_main + r"\scripts\process"
cwd_scripts_visual = cwd_main + r"\scripts\visualisation"
cwd_reports = cwd_project + r"\reports"
cwd_figures = cwd_project + r"\reports\figures"
cwd_data_str = cwd_project + r"\data\1_structured"
cwd_data_filt = cwd_project + r"\data\2_filtered"
cwd_data_proc = cwd_project + r"\data\3_processed"


                      
#%%	

#Definition of extent - frame for mapping
dist = plot/2
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


