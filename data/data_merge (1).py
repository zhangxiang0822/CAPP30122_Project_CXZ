###===============================================
## This script will merge all the first-stage-cleaned
## data to our final database
###===============================================

import numpy as np
import pandas as pd
import chardet
from math import sin, cos, sqrt, atan2, radians
import geopy.distance
from state_convertor import state_convertor

###=====================================================
## Load in the first three social_demo dataset to merge
###=====================================================
def merge_social_demo(acs_filename, aqi_filename, crime_filename):
	'''
	This function will merge the first three social_demographic datsets:
	American Community Survey, Air quality index and crime data
	Input:
		three filenames 
	Output:
		df_merged: a pandas dataframe of the merged dataset
	'''
	## load in acs data
	df_acs = pd.read_csv(acs_filename, sep = ",")

	## load in aqi data
	df_aqi = pd.read_csv(aqi_filename)
	df_aqi["NAME"] = df_aqi.County + " County, " + df_aqi.State

	## load in crime data
	df_crime = pd.read_csv(crime_filename)
	df_crime = df_crime.rename(index = str, columns = {"FIPS_ST": "state", "FIPS_CTY":"county"})

	### Merging three datasets
	## merging aqi and acs
	df_merged = pd.merge(df_acs, df_aqi, how = "left", on = ["NAME"])

	## merging acs and crime data
	df_merged = pd.merge(df_merged, df_crime, how =  "left", on  = ["state", "county"])
	    
	# load in lonlat dataset
	df_latlon = pd.read_csv('uslatlon.txt').loc[:, ["FIPS", "Latitude", "Longitude"]]
	df_latlon["state"] = df_latlon.loc[:, ["FIPS"]].apply(lambda x: int(str(x.FIPS)[:-3]), axis = 1)
	df_latlon["county"] = df_latlon.loc[:, ["FIPS"]].apply(lambda x: int(str(x.FIPS)[-3:]), axis = 1)
	df_latlon = df_latlon.drop(["FIPS"], axis = 1)

	# merge latlon dataset with the merged dataset
	df_merged = pd.merge(df_merged, df_latlon, on = ["state", "county"])

	return df_merged

## =======================================================================================
### Now we will use the latitude and longitude to aprpoximate counties without AQI data
## =======================================================================================
def fill_missing_aqi(df_merged):
	'''
	This function will use the neareset neighbor mechanism to fill out
	the missing air quality index data with that of the geographically-closest
	county
	Input:
		df_merged: merged pandas dataframe
	Output:
		df_merged: merged pandas dataframe
	'''

	county_wo_aqi = df_merged[pd.isnull(df_merged.State)].NAME.values    # counties without air quality index
	county_w_aqi = df_merged[-pd.isnull(df_merged.State)].NAME.values	 # counties with air quality index data
	dict_county_w_aqi = {}
	dict_county_wo_aqi = {}
	aqi_cols = [c for c in df_merged.columns if "aqi_" in c]

	## construct the dictionary of counties with air quality index data for sorting later
	for c in county_w_aqi:
	    dict_county_w_aqi[c] = (float(df_merged[df_merged.NAME == c].Latitude.values),
	                            float(df_merged[df_merged.NAME == c].Longitude.values))
	    
	for c in county_wo_aqi:
	    (lat, lon) = (float(df_merged[df_merged.NAME == c].Latitude.values),
	                            float(df_merged[df_merged.NAME == c].Longitude.values))
	    
	    ## we use the sorting so that the complexity will be O(nlogn)
	    lst_sorted = sorted(dict_county_w_aqi, 
	                       key = lambda k: (dict_county_w_aqi[k][0] - lat)**2 + 
	                        (dict_county_w_aqi[k][1] - lon)**2
	                       )
	    nearest_county = lst_sorted[0]
	    nearest_ind = df_merged[df_merged.NAME == nearest_county].index
	    print(nearest_county)
	    
	    df_merged.loc[df_merged.NAME == c, aqi_cols] = \
	        df_merged.loc[df_merged.NAME == nearest_county, aqi_cols].values


	### some cleaning of the air quality index data
	df_merged = df_merged.drop(["Unnamed: 0_y", "State", "County"], axis = 1)
	df_merged = df_merged.dropna(axis = 0, how = "any")
	## creating the good air-quality days
	aqi_cols_good = [c for c in aqi_cols if "aqi_good" in c]
	aqi_cols_bad = [c for c in aqi_cols if "aqi_bad" in c]
	df_merged["aqi_good"] = df_merged.loc[:, aqi_cols_good].mean(axis = 1)
	df_merged["aqi_bad"] = df_merged.loc[:, aqi_cols_bad].mean(axis = 1)
	crime_cols = [c for c in df_merged.columns if "crime_rate" in c]
	df_merged["crime_rate"] = df_merged.loc[:, crime_cols].mean(axis = 1) 

	return df_merged   

## ========================================================
## Now we will merge the weather data
## ========================================================
def merge_weather(weather_filename, df_merged):
	'''
	This function will merge the weather data to the main dataset
	Input:
		weather_filename: filename of cleaned weather data
	Output:
		df_merged: pandas dataframe of the merged dataset

	'''

	df_weather = pd.read_csv(weather_filename, sep = ",")

	## create the dictionary of weather station for faster sorting later
	dict_weather = {}
	for i in range(len(df_weather)):
	    dict_weather[i] = (
	        df_weather.iloc[i].Latitude, 
	        df_weather.iloc[i].Longitude
	    )

	month_col = ["Jan", "Feb", "Mar", 
	             "Apr", "May", "Jun",
	             "Jul", "Aug", "Sep", 
	             "Oct", "Nov", "Dec"]
	var_col = ["avg_temp", "max_temp", "min_temp", "prcp", "snow"]
	weather_var_col = []
	for month in month_col:
	    for var in var_col:
	        weather_var_col.append(str(month + "_" + var))
	return df_merged


## ===========================================
## using latitude and longitude to match 
## weather monitoring stations to counties 
## based on the nearest neighbor principle
## ===========================================
def find_nearest_station(df_merged):
	'''
	This function will find the neareset station and use the information of the nearest station
	as that of county's

	'''
	weather_cols = {m: [] for m in weather_var_col}
	for i in range(len(df_merged)):
	    lat, lon = df_merged.iloc[i].Latitude, df_merged.iloc[i].Longitude
	    lst_sorted = sorted(dict_weather, 
	                       key = lambda k: (dict_weather[k][0] - lat)**2 + (dict_weather[k][1] - lon)**2
	                       )
	    nearest_station_id = lst_sorted[0]
	    for m in weather_var_col:
	        weather_cols[m].append(df_weather.iloc[nearest_station_id][m])
	    print(nearest_station_id)


	weather_cols = pd.DataFrame(weather_cols)
	df_merged = pd.concat([df_merged.reset_index(drop = True), weather_cols.reset_index(drop = True)], axis = 1)
	df_merged["winter_avg_temp"] = \
		(df_merged.Dec_avg_temp + df_merged.Jan_avg_temp + df_merged.Feb_avg_temp) / 3
	df_merged["summer_avg_temp"] = \
		(df_merged.Jun_avg_temp + df_merged.Jul_avg_temp + df_merged.Aug_avg_temp) / 3
	df_merged["annual_avg_temp"] = \
		df_merged[[month +"_avg_temp" for month in month_col]].mean(axis = 1)

	return df_merged

def mapping_st_region(df_merged):
	'''
	This function will create categorical variables: state_name and region
	'''
	region_state = {
	    "Region":[],
	    "State_name":[]
	    
	}
	for i in range(df_merged.shape[0]):
	    state_fips = df_merged.iloc[i].ST
	    region_state["Region"].append(state_convertor[state_fips]["state_abbr"])
	    region_state["State_name"].append(state_convertor[state_fips]["state_cd"])
	    
	region_state = pd.DataFrame(region_state)

	df_merged = pd.concat([df_merged.reset_index(drop = True), region_state.reset_index(drop = True)], axis = 1)

	return df_merged


## ===============================================
## merge census data
## ===============================================
def merge_census(census_filename, df_merged):
	'''
	This function will merge census dataset
	'''

	df_census = pd.read_csv(census_filename, sep = ",")
	df_census = df_census.drop(["Unnamed: 0", "Urban", "NAME", 
	                            'Hispanic_Latino', 'White', 'Black', 'Asian'], axis = 1)
	df_census = df_census.rename(columns={"Hispanic_Latino_share": "Hispanic_Latino",
	                                      "White_share": "White",
	                                      "Black_share": "Black",
	                                     "Asian_share": "Asian"})
	df_merged = pd.merge(df_merged, df_census, 
	                     #how =  "left", 
	                     on  = ["state", "county"])
	df_merged["Share_over65"] = df_merged.Pop_over65 / df_merged.Population
	df_merged["Share_under18"] = df_merged.Pop_under18 / df_merged.Population
	## we also wanna have a column to show the largest racial composition
	race_list = ['Hispanic_Latino', 'White', 'Black', 'Asian']
	largest_race = {"largest_race": []}
	for i in range(df_merged.shape[0]):
	    row = df_merged.iloc[i]
	    rac = row[[race for race in race_list]].idxmax()
	    #print(rac)
	    largest_race["largest_race"].append(rac)

	largest_race = pd.DataFrame(largest_race)
	df_merged = pd.concat([df_merged.reset_index(drop = True), largest_race.reset_index(drop = True)], axis = 1)

	return df_merged

## ===============================================
## merge transportation data
## ===============================================
def merge_airport(airport_filename, df_merged):
	'''
	This function will merge the airport dataset
	'''
	df_airport = pd.read_csv(airport_filename)
	df_airport = df_airport.loc[(df_airport.type == "large_airport") | (df_airport.type == "medium_airport")]

	df_airport = df_airport.rename(columns = {"name": "airport",
	                                         "latitude_deg": "Latitude",
	                                         "longitude_deg": "Longitude"})
	df_airport = df_airport[["airport", "Latitude", "Longitude"]]
	df_airport["Latitude"] = abs(df_airport["Latitude"])
	df_airport["Longitude"] = abs(df_airport["Longitude"])

	dict_airport = {}
	for i in range(df_airport.shape[0]):
	    dict_airport[i] = (
	        df_airport.iloc[i].Latitude, 
	        df_airport.iloc[i].Longitude
	    )

	airport_cols = {"airport":[], "dist_airport":[]}
	for i in range(len(df_merged)):
	    lat, lon = df_merged.iloc[i].Latitude, df_merged.iloc[i].Longitude
	    lst_sorted = sorted(dict_airport, 
	                       key = lambda k: (dict_airport[k][0] - lat)**2 + (dict_airport[k][1] - lon)**2
	                       )
	    nearest_airport = lst_sorted[0]
	    lat_airport, lon_airport = df_airport.iloc[nearest_airport]["Latitude"], df_airport.iloc[nearest_airport]["Longitude"]
	    coords_1 = (lat, lon)
	    coords_2 = (lat_airport, lon_airport)
	    airport_cols["dist_airport"].append(geopy.distance.vincenty(coords_1, coords_2).km)
	    airport_cols["airport"].append(df_airport.iloc[nearest_airport]["airport"])
	    print(nearest_airport)


	airport_cols = pd.DataFrame(airport_cols)
	df_merged = pd.concat([df_merged.reset_index(drop = True), airport_cols.reset_index(drop = True)], axis = 1)

	return df_merged

if __name__ == "__main__":
    acs_filename = "./acs_data/ACS_data.txt"
    aqi_filename = "./aqi_data/aqi_data_clnd.csv"
    crime_filename = "./crime_data/crime_data_clnd.csv"
    weather_filename = "./weather_data/climate_by_station.txt"
    census_filename = "./census_data/census_data.txt"
    airport_filename = "./airport_data/airport_data.csv"

    df_merged = merge_social_demo(acs_filename, aqi_filename, crime_filename)
    df_merged = fill_missing_aqi(df_merged)
    df_merged = merge_weather(weather_filename, df_merged)
    df_merged = find_nearest_station(df_merged)
    df_merged = mapping_st_region(df_merged)
    df_merged = merge_census(census_filename, df_merged)
    df_merged = merge_airport(airport_filename, df_merged)

	df_merged.to_csv("./database/database_cleaned.csv")

