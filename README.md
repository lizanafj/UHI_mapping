# UHI_mapping
_Atmospheric urban heat island mapping using citizen weather data._

This project is further detailed in the following scientific article: 

  **reference**


## Overview
This project is an open-source procedure to extract, filter and analysis urban climate at a very high spatio-temporal resolution using crowdsourced citizen weather data from platforms such us Netatmo or Wunderground.
It comprises a set of data pre-processing and analytic techniques to ensure citizen weather data meet overall quality goals and perform standardised city diagnosis.

![uhi](https://github.com/lizanafj/UHI_mapping/blob/main/references/UHI_London_hottestdays_1.gif)

## Requirements to use UHI_mapping

### Python version
 - Python 3.8+

### Installing development requirements
------------

    pip install -r requirements.txt


## How to use **UHI_mapping**?

The workflow is divided into different Jypyter Notebooks **see /notebooks** to guide the workflow.

- **Notebook 00_NewProject** - Define and create the new project directory to save and process data. 
- **Notebook 01_DataExtraction_Netatmo** - Extract weather data (*.csv) from Netatmo 
- **Notebook 02_DataPre-processing** - Different cleaning and quality control techniques to eliminate outliers
- **Notebook 03_DataAnalytics_Preparatory** - 1/3 data analysis: calculate rural temperature profile (baseline) and Cooling Degree Hours (CDHs)
- **Notebook 04_DataAnalytics_HourlyDiagnosis** - 2/3 data analysis: calculate hourly UHI intensity 
- **Notebook 05_DataAnalytics_AnnualDiagnosis** - 3/3 data analysis: identificaiton of persistent hot spots using CDHs


## The directory structure
------------

The directory structure of UHI_mapping project looks like this: 

```
UHI_mapping/
│ 
├── LICENSE 				<- GPL-3.0 license
├── README.md
├── requirements.txt   			<- The requirements file for reproducing the analysis environment
│          		
├── notebooks				<- Jupyter notebooks to guide the workflow
│   ├─ 00_NewProject.ipynb      	
│   ├─ 01_DataExtraction_Netatmo.ipynb        		
│   ├─ 02_DataPre-processing.ipynb 
│   ├─ 03_DataAnalytics_Preparatory.ipynb 
│   ├─ 04_DataAnalytics_HourlyDiagnosis.ipynb 
│   ├─ 05_DataAnalytics_AnnualDiagnosis.ipynb     		
│             		
├── projectname/			<- Database divided by project (city)
│   ├─ cityname1/
│   	├─ data/
│	   ├─ 0_raw
│	      ├─ temp				
│	   ├─ 1_structured
│	   ├─ 2_filtered
│	   ├─ 3_processed    
│   	├─ reports/
│	   ├─ figures/  
│   	├─ config.py                    		
│   ├─ cityname2/
│	├─...
│
├── references         			<- manuals and all other explanatory materials.          
│
├── scripts/				<- Source code for use in this project
│	├─ data/			<- Scripts to download or generate data
│	   ├─ functions/
│	   ├─ A1_getstationsdata_netatmo.py
│	   ├─ A2_getmeasure_netatmo.py
│	   ├─ projectdata.json
│	├─ process/			<- Scripts for pre-processing (cleaning and quality control) and processing (analytics)
│	   ├─ functions/
│	   ├─ B_DataPre-processing
│	   ├─ C1_DataAnalytics_1
│	   ├─ projectdata_p.json
│	├─ visualisation/		<- Scripts to create exploratory and results oriented visualizations
│	   ├─ functions/
│
└──
```
