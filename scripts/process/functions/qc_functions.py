# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 10:58:51 2022

@author: engs2371

Functions for quality control:

"""

import pandas as pd 
import numpy as np

#statistics
import scipy.stats as stats

#Qn scale estimator proposed by Rousseeuw and Croux as an alternative to the MAD (for modified z-score)
from statsmodels.robust.scale import qn_scale as qn #https://www.statsmodels.org/dev/_modules/statsmodels/robust/scale.html

#t-student distribution and normal distribution
from scipy.stats import t
from scipy.stats import norm 

#FOR DISTANCES BETWEEN COORDINATES
from geopy.distance import geodesic


#%%

##Example of functions: 

def test_name(name):
    """
    This function greets to
    the person passed in as
    a parameter
    """
    print("Hello, " + name + ". Good morning!")
    


#%%

######################################################################################################################

#### QC_I1 - Contaminated data - Data type

######################################################################################################################

def QC_I1_datatype(data):
    """
    This function analyzes the data type in the sample.
    
    """
    values = data.count().sum()/data.size
    values = values.round(2)
    values = values*100
    columns = len(data.columns)
      
    print("")
    print("Shape: ", data.shape)
    print("Size: ", data.size, " - ", "non- nan values: ", data.count().sum())
    print("Percentage of non- nan values: ",values,"%")
    print("Columns: ",columns)
    print("Dtype: ", data.dtypes.value_counts())
    #print("Breakdown of Dtype: ", data.info())
    
    
    
    
#%%

######################################################################################################################

#### QC_I3	-  Outliers 1	-  Gross-error limit test	-  Threshold: -40ºC and 60ºC

######################################################################################################################

def QC_I3_limittest(data):
    """
    This function eliminates data outside the following threshold: -40ºC and 60ºC.
    
    """
 
    data = data[((data > -40) & (data < 60 ))]
    
    return data

    
#%%


######################################################################################################################

#### QC_I4	-  Inconsistent data	-  Temporal consistency: slope test -  Threshold: 20ºC/h

######################################################################################################################

def QC_I4_slopetest(data):
    """
    This function eliminates data with a gradient higher than 20ºC/h.
    
    """
    #Calculation slope
    slope = abs(data.diff(periods=1, axis=0))
    
    #mask considering slope threshold and nans as true
    data = data[((slope < 20) | (pd.isna(slope)))]

    return data

    
#%%

######################################################################################################################

#### QC_I5	- Inconsistent data	 -  Temporal consistency: persistence test 	-  Timeframe: 6h

######################################################################################################################

def QC_I5_consistencytest(data):
    """
    This function eliminates data with a constant value longer than 6 hours.
    
    """
    #Slope
    slope = abs(data.diff(periods=1, axis=0))
    
    # True if slope is cte
    slope = ((slope < 0.005) | (pd.isna(slope)))
    
    # rolling sum, threshold 6 - if the value is repearted more then 6 times == 6
    slope1 = slope.rolling(6,min_periods=1).sum()
   
    """
    #old code v1
    for column in slope1:
        for i in range(6,len(slope1)):
            value = slope1[column].iloc[i,]   
            if value == 6.0:
                slope1[column][i-6:i+1] = np.nan
    """
    """
    #old code v2
    step=0
    for column in slope1:
        step = step +1
        for i in range(6,len(slope1)):

            value = slope1[column].iloc[i]   
            print(step,column,i,value)

            if value == 6.0:
                print(value)
                print(slope1[column][i-6:i+1])
                slope1[column][i-6:i+1] = np.nan
                print(slope1[column][i-6:i+1])
    """
    
    for column in range(len(slope1.columns)):
        for i in range(6,len(slope1)):
            value = slope1.iloc[i,column]
            if value == 6.0:
                slope1.iloc[i-6:i+1,column] = np.nan
                
    #slope1a = slope1[(slope1<6)]
    
    #True if el valor se repite más de 6 veces
    slope2 = slope1.isna()
    
    data2 = data.mask(slope2==True,np.nan)

    return data2

    
#%%

######################################################################################################################

#### QC_G4	- Duplicate data	Duplicate CWS/OWS

######################################################################################################################
# Duplicate stations (ID, lat, long)

#cutOff How much stations are allowed to have the same coordinates/duplicates
#cutOff= 1 # Not introduced

#Flag values with True
def QC_G4_duplicate(data):
    """
    This function eliminates data with duplicate values or missing values according to id, long and lat.
    
    """
    data1 = data
    
    #a - missing value p_id, lon, lat
    data1 = data1.replace('', np.nan) 
    data1["a"] = data1["module_final"].isnull()+data1["long"].isnull()+data1["lat"].isnull()

    #b - same value for long - lat
    data1["b"]= (data1["long"]==data1["lat"])

    #c - check for all file (duplicated) - mantaining the first one
    data1["c"] = data1[["_id","module_final","long","lat"]].duplicated()

    #d - check for long - lat (duplicated) - mantaining the first one - step eliminated (for example: same building, different sensors per dwelling)
    data1["d"] = np.nan #data1[["long","lat"]].duplicated()
    
    #M1 - report
    data1["M1"] = data1["a"]+data1["b"]+data1["c"]+data1["d"]

    a = (data1["a"]==True).sum()
    b = (data1["b"]==True).sum()
    c = (data1["c"]==True).sum()
    d = (data1["d"]==True).sum()
    M1 = (data1["M1"]==True).sum()
    M1_perc = 1-(data1["M1"]==True).sum()/data1["module_final"].count()

    d = {'Missing values': [a], 'Same values': [b], 'All duplicated': [c], 'Long-Lat duplicated': [d], 'M1': [M1], 'M1_perc': [M1_perc]}
    report_M1 = pd.DataFrame(data=d)
    
    print("Report of Flag values for step M1")
    print(report_M1)

    data1 = data1.drop(["a","b","c","d"], axis=1)

    return data1,report_M1

    
#%%

######################################################################################################################

#### QC_G5	- Group outliers 2	 - Statistical analysis: group data distribution	mod_z_score_qn

######################################################################################################################

def QC_G5_distribution(weather_data, z_score, t_distribution,low, high):
    """
    Normal distribution (or Student-t distribution if stations <100) is used to identify outliers: 
    lower and upper ends of the distribution at each time step. 

    z_score = alternatives:

    "z_score" = (t- mean(t))/std
    "mod_z_score_mad"=(t - median())/MAD
    "mod_z_score_qn"= (t - median())/Qn

    """
    
    weather_M2 = weather_data
    
    weather_M2_Zscore = pd.DataFrame()
    
    #Standard deviation (std)
    #https://vitalflux.com/standard-deviation-sample-population-python-code
    #ddof=1 means: n - 1 : The idea is that the calculation of standard deviation of sample includes a little bias due to the fact that the deviation is 
    #calculated based on the sample mean rather than the population mean.
    #Thus, the bias is removed by subtracting 1 from the sample size. ##### NOSOTROS USAMOS ddof=0 

    if z_score=="z_score":
        #z-score
        for i in range(0,len(weather_M2)):
            appenddata = (weather_M2.iloc[[i]] - weather_M2.iloc[i].mean(skipna=True))/weather_M2.iloc[i].std(skipna=True,ddof=0)  #Always, quitar nan values
            weather_M2_Zscore = pd.concat([weather_M2_Zscore,appenddata],axis=0)
        #otra forma de calculo directo z-score para media y std population
        #weather_M2_Zscore1 = stats.zscore(weather_M2.iloc[i].dropna())
        
    elif z_score=="mod_z_score_mad":   
        #Mod_z-score usando MAD
        for i in range(0,len(weather_M2)):
            appenddata = 0.6745*(weather_M2.iloc[[i]] - weather_M2.iloc[i].median(skipna=True))/weather_M2.iloc[i].mad(skipna=True)  #Always, quitar nan values
            weather_M2_Zscore = pd.concat([weather_M2_Zscore,appenddata],axis=0)
        
    elif z_score=="mod_z_score_qn":
        #mod_Z-score usando Qn
        #Qn scale estimator proposed by Rousseeuw and Croux as an alternative to the MAD
        #https://www.statsmodels.org/dev/_modules/statsmodels/robust/scale.html
        for i in range(0,len(weather_M2)):
            appenddata = (weather_M2.iloc[[i]] - weather_M2.iloc[i].median(skipna=True))/qn(weather_M2.iloc[i].dropna())   #Always, quitar nan values
            weather_M2_Zscore = pd.concat([weather_M2_Zscore,appenddata],axis=0)
    
    else: 
        print("no match")
        
    weather_M2_Zscore_no_outliers = weather_M2_Zscore.copy() #mandatory to add copy() to avoid duplicate the dataframe - take care 


    if t_distribution==True:
        #t-student distribution
        for i in range(0,len(weather_M2_Zscore_no_outliers)):
            n = weather_M2_Zscore_no_outliers.iloc[i].count() -1  
            weather_M2_Zscore_no_outliers.iloc[i] = weather_M2_Zscore_no_outliers.iloc[i].mask((weather_M2_Zscore_no_outliers.iloc[i]<t.ppf(low,df=n)) | (weather_M2_Zscore_no_outliers.iloc[i]>t.ppf(high,df=n)))
    elif t_distribution==False:  
        #normal distribution
        for i in range(0,len(weather_M2_Zscore_no_outliers)):
            weather_M2_Zscore_no_outliers.iloc[i] = weather_M2_Zscore_no_outliers.iloc[i].mask((weather_M2_Zscore_no_outliers.iloc[i]<norm.ppf(low)) | (weather_M2_Zscore_no_outliers.iloc[i]>norm.ppf(high)))
            #weather_M2_Zscore_no_outliers = weather_M2_Zscore[(weather_M2_Zscore>norm.ppf(low)) & (weather_M2_Zscore<norm.ppf(high))]
    else: 
        print("no match")
    
    #mask to select TRUE VALUES
    weather_M2 = weather_M2[weather_M2_Zscore_no_outliers.notnull()==True]

    return weather_M2_Zscore, weather_M2_Zscore_no_outliers,weather_M2 
         














#%%	


######################################################################################################################

#### QC_G6	- Group outliers 4	Statistical analysis: constant errors	Threshold: Outliers > 25%

######################################################################################################################

#Trust or not trust stations

def QC_G6_trust(weather_data,outliers, cutOff, time):
    
    """
    Stations with outliers >20% of data are considered erroneous and eliminated. 
    This is formerly set per month.
    
    cutOff=0.2, monthly basis

    Data of sensors with constant errors are eliminated.

    
    
    """
    
    #Percentage of data
    removed_data = outliers.resample(time).count()
    size_data = outliers.resample(time).size()
    fraction = removed_data.div(size_data.values, axis=0)
    
    fraction1 = (fraction>cutOff).sum(axis=0).to_frame()
    fraction1 = fraction1.rename(columns={0:"months"})
    
    #Geg "_id" stations with >20% of data per month missing
    fraction1["months"] = fraction1[(fraction1["months"]>0)]
    fraction1 = fraction1.dropna().reset_index()
    
    #List of stations "_id" to remove from m2. 
    List_M3 = []
    List_M3 = list(fraction1["index"].dropna())
    
    weather_M3 = weather_data
    weather_M3 = weather_M3.drop(List_M3, axis=1)
    
    return weather_M3



#%%	


######################################################################################################################

#### QC_G7	- Group outliers 3	Statistical analysis: group temporal correlation	Threshold: Pearson correlation coefficient <0.9

######################################################################################################################

def QC_G7_tcorrelation(weather_data,cutOff):
    
    """
    Temporal correlation between each station and the median of all stations is carried out 
    for a specified period of time, in a monthly basis. 

    Type of Pairwise comparisons:
    -Pearson
    -Spearman
    -Kendall

    We use Pearson +-1 (perfect), 0 (wrong)

    #https://www.geeksforgeeks.org/python-pandas-dataframe-corr/

    #correlation corr()


    The Pearson correlation coefficient (R)
    between each individual station and the median of CWS is calculated for each month. 
    If the correlation is lower than 0.9, the data in month m of the considered station j are set to NaN:

    """
    
    #Database of data to operate (copy to original)
    weather_M4_help = weather_data.copy()

    #get month in a new column
    weather_M4_help["month"] =  weather_M4_help.index.month

    #List of existing months. 
    List_month = []
    List_month = list(weather_M4_help["month"].drop_duplicates().dropna())

    #Reuse column of month to calculate median
    weather_M4_help = weather_M4_help.rename(columns = {"month":"median"})
    weather_M4_help["median"] = np.nan

    #Calculation of median (without acounting the median column)
    for i in range(0,len(weather_M4_help)):
        weather_M4_help["median"].iloc[i] = weather_M4_help.drop(labels=["median"],axis=1).iloc[i].median(skipna=True)

    #final loop to eliminate columns per month with pearson<0.9 (cutOff)
    weather_M4 = pd.DataFrame()

    for i in List_month:
        weather_M4_help1 = pd.DataFrame()
        weather_M4_help1 = weather_M4_help[(weather_M4_help.index.month==i)]
        correlation = abs(weather_M4_help1.corr(method='pearson'))
        correlation = correlation["median"].drop(labels=["median"],axis=0).to_frame()
        
        #raw data without column=median to be cleaned and append
        weather_M4_help1 = weather_M4_help1.drop(labels=["median"],axis=1)
        
        #Geg "_id" stations with pearson<0.9 of data per month missing
        correlation1 = correlation[(correlation["median"]<cutOff)]
        correlation1 = correlation1.reset_index()
        
        #List of stations "_id" to remove from m2.
        List_M4 = []
        List_M4 = list(correlation1["index"].dropna())
            
        print("month",i,"-- Id to eliminate: ", List_M4)
        
        #eliminate Id of stations with pearson <0.9
        weather_M4_help1 = weather_M4_help1.drop(List_M4, axis=1)
        
        #combine previous data mwith new cleaned data of month i
        weather_M4 = pd.concat([weather_M4,weather_M4_help1])
    
    return weather_M4











#%%	


######################################################################################################################

#### QC_G8	- Missing data	Filling gaps by interpolation 	
 

######################################################################################################################



def QC_G8_interpolation(data,threshold):
    """
    #INTERPOLATION USING FILL GAP - LIMITED TO 2 GAP (MAXlength/threshold = 2)
    
    threshold = 2 #by default
    """
    
    #https://docs.scipy.org/doc/scipy/tutorial/interpolate.html
    #['linear', 'time', 'index', 'values', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'barycentric', 'krogh', 'spline', 'polynomial', 'from_derivatives', 'piecewise_polynomial', 'pchip', 'akima', 'cubicspline']. Got 'cubic spline' instead.


    CWS_UrbanClimate_all_QC_G8 = data.interpolate(method="cubicspline",limit=2,limit_area="inside") #rellenar huecos sencillo. Límit 2
    
    #eliminate interpolation if nan is longer than 2 values
    for c in data:
        mask = data[c].isna()
        x = (mask.groupby((mask != mask.shift()).cumsum()).transform(lambda x: len(x) > threshold )* mask)
        CWS_UrbanClimate_all_QC_G8[c] = CWS_UrbanClimate_all_QC_G8.loc[~x, c]
        
    return CWS_UrbanClimate_all_QC_G8









#%%	


#for furture development/testing

######################################################################################################################

#### QC_G9	- Group outliers 5	Clustering analysis: grouping extreme profiles 	
 

######################################################################################################################


#QC_G9. CLUSTERING - PENDING

"""
#Clustering analysis: grouping extreme profiles 


import math
# Preprocessing
from sklearn.preprocessing import MinMaxScaler
# Algorithms
#from minisom import MiniSom
#from tslearn.barycenters import dtw_barycenter_averaging
#from tslearn.clustering import TimeSeriesKMeans
#from sklearn.cluster import KMeans

from sklearn.decomposition import PCA




"""




















