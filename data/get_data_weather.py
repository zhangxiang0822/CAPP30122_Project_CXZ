import numpy as np
import pandas as pd

column_names = ['latitude','longitude','elevation','state','name']

def read_excel(file_name):
	'''
	Read the climate data of each station from excel document and store
	the data into a pandas dataframe
	'''
	df = pd.read_excel(file_name, index_col = 0)
	return df

def get_monthly_temp(df):
	'''
	The function is used to clean the dataframe and get the data of the 
	monthly average temperature, maximum temperature and minimum temperature,
    then return a cleaned dataframe of monthly temperature

    Input:
    df: the original dataframe read from the excel document

    Return:
    df_temp: the cleaned dataframe contains the monthly temperature information.
	'''
    for index,row in df.iterrows():
        for i in range(12):
            lenth = len(row[i])-1
            data = row[i][:lenth]
            if data == '-7777':
                row[i] = '0'
            elif data in ['-9999','-6666','-5555']:
                row[i] = 'NA'
            else:
                temp = round(int(data) * 0.1,1)
                row[i] = str(temp)
    return df_temp

def get_monthly_prcp(df):
	'''
	The function is used to clean the dataframe and get the data of the 
	monthly precipitation then return a cleaned dataframe of monthly precipitation

    Input:
    df: the original dataframe read from the excel document

    Return:
    df_prcp: the cleaned dataframe contains the monthly precipitation information.
	'''	
    for index,row in df.iterrows():
        for i in range(12):
            lenth = len(row[i])-1
            data = row[i][:lenth]
            if data == '-7777':
                row[i] = '0'
            elif data in ['-9999','-6666','-5555']:
                row[i] = 'NA'
            else:
                prcp = round(int(data) * 0.01,2)
                row[i] = str(prcp)
    return df_prcp

def get_monthly_snow(df):
	'''
	The function is used to clean the dataframe and get the data of the 
	monthly snow then return a cleaned dataframe of monthly snow

    Input:
    df: the original dataframe read from the excel document

    Return:
    df_snow: the cleaned dataframe contains the monthly snow information.
	'''	
    for index,row in df.iterrows():
        for i in range(12):
            lenth = len(row[i])-1
            data = row[i][:lenth]
            if data == '-7777':
                row[i] = '0'
            elif data in ['-9999','-6666','-5555']:
                row[i] = 'NA'
            else:
                snow = round(int(data) * 0.1,1)
                row[i] = str(snow)
    return df_snow

def get_monthly_dd(df):
	'''
	The function is used to clean the dataframe and get the data of the 
	monthly cooling degree day and heating degree day then return a cleaned 
	dataframe

    Input:
    df: the original dataframe read from the excel document

    Return:
    df_dd: the cleaned dataframe contains the monthly CDD/HDD information.
	'''		
    for index,row in df.iterrows():
        for i in range(12):
            lenth = len(row[i])-1
            data = row[i][:lenth]
            if data == '-7777':
                row[i] = '0'
            elif data in ['-9999','-6666','-5555']:
                row[i] = 'NA'
            else:
                dd = int(data)
                row[i] = str(dd)
    return df_dd


mly_tavg = read_excel("mly-tavg-normal.xlsm")
mly_tmax = read_excel("mly-tmax-normal.xlsm")
mly_tmin = read_excel("mly-tmin-normal.xlsm")
mly_htdd = read_excel("mly-htdd-normal.xlsm")
mly_cldd = read_excel("mly-cldd-normal.xlsm")
mly_prcp= read_excel("mly-prcp-normal.xlsm")

temp_stations = read_excel("temp-inventory.xlsm")
temp_stations = temp_stations[column_names]

prcp_stations = read_excel("prcp-inventory.xlsm")
prcp_stations = prcp_stations[column_names]

snow_stations = read_excel("snow-inventory.xlsm")
snow_stations = snow_stations[column_names]

average_temp = get_monthly_temp(mly_tavg)
max_temp = get_monthly_temp(mly_tmax)
min_temp = get_monthly_temp(mly_tmin)
month_prcp = get_monthly_prcp(mly_prcp)
month_cdd = get_monthly_dd(mly_cldd)
month_hdd = get_monthly_dd(mly_htdd)
month_snow = get_monthly_snow(mly_snow)

# Since the station information of precipitaion data is different from
# that of temperature data, thus using the index of temprature data to 
# match the precipitation data.

match_mth_prcp = month_prcp.loc[average_temp.index]
index = match_mth_prcp.index
columns = match_mth_prcp.columns
climate_df = pd.DataFrame(index = index, columns = columns)
index_snow = month_snow.index

for index, row in climate_df.iterrows():
    for i in range(12):
        temp_avag = average_temp.loc[index][i]
        temp_max = max_temp.loc[index][i]
        temp_min = min_temp.loc[index][i]
        cdd = month_cdd.loc[index][i]
        hdd = month_hdd.loc[index][i]
        prcp = match_mth_prcp.loc[index][i]
        if index in index_snow:
            snowfall = month_snow.loc[index][i]
        else:
            snowfall = '0.0'
        row[i] = (temp_avag,temp_max,temp_min,cdd,hdd,prcp,snowfall)

climate_station = temp_stations.join(climate_df)

climate_station.to_csv("climate_by_station.csv")
