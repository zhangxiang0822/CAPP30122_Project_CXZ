from bs4 import BeautifulSoup
import urllib.request
import requests
import zipfile
import re
import pandas as pd


url = "aqs.epa.gov/aqsweb/airdata/download_files.html#AQI"
file_prefix = "annual_aqi_by_county_"
download_prefix = "https://aqs.epa.gov/aqsweb/airdata/"
download_dir = "./download_zips/"
data_dir = "./aqi_data/"


## =====================================================
## a set of functions to get air-quality data from the web
## =====================================================

def get_zipfile_lst(url, file_prefix):
	r  = requests.get("https://" + url)

	data = r.text

	soup = BeautifulSoup(data)

	zipfile_lst = []
	for link in soup.find_all('a', href = re.compile(file_prefix)):
		zipfile = link.get('href')
		print(zipfile)
		zipfile_lst += [zipfile]

	return(zipfile_lst)

## download zipfile 

def download_zipfile(zipfile_lst, download_prefix, download_dir):
	for filename in zipfile_lst:
		download_url = download_prefix + filename
		urllib.request.urlretrieve(download_url, download_dir+filename)

## unzip datafiles
def unzip_data(zipfile_lst, data_dir):
	for filename in zipfile_lst:
		zip_ref = zipfile.ZipFile(download_dir + filename, 'r')
		zip_ref.extractall(data_dir)
		zip_ref.close()


### ==================================================
## download the air quality data
### ==================================================
zipfile_lst = get_zipfile_lst(url, file_prefix)
download_zipfile(zipfile_lst, download_prefix, download_dir)
unzip_data(zipfile_lst, data_dir)

## ====================================================
## clean the air quality data
## ====================================================
yrs_lst = [ 2014, 2015, 2016, 2017]
## Calculating the ratio of good/modereate/unhealty_SG/unhealthy/very_unhealthy/hazardous
var_lst = [
 'Good Days',
 #'Moderate Days',
 #'Unhealthy for Sensitive Groups Days',
 #'Unhealthy Days',
 'Very Unhealthy Days'#,
 #'Hazardous Days'
]

## read in data
df_aqi = pd.read_csv("./aqi_data/annual_aqi_by_county_2013.csv")
for var in var_lst:
    df_aqi[var +" ratio" + str(2013)] = df_aqi[var] / df_aqi['Days with AQI']
## only keeping relative columns
column_lst = [var +" ratio" + str(2013) for var in var_lst] + ["State", "County"]
df_aqi = df_aqi.filter(items = column_lst)
    
for i in yrs_lst:
    df_new = pd.read_csv("./aqi_data/annual_aqi_by_county_" + str(i) + ".csv")
    for var in var_lst:
        df_new[var +" ratio" + str(i)] = df_new[var] / df_new['Days with AQI']
    ## only keeping relative columns
    column_lst = [var +" ratio" + str(i) for var in var_lst] + ["State", "County"]
    df_new = df_new.filter(items = column_lst)
    df_aqi = pd.merge(df_aqi, df_new, on = ["State", "County"])

df_aqi.rename(columns = {
    "Good Days ratio2013": "aqi_good_2013",
    "Good Days ratio2014": "aqi_good_2014",
    "Good Days ratio2015": "aqi_good_2015",
    "Good Days ratio2016": "aqi_good_2016",
    "Good Days ratio2017": "aqi_good_2017",
    "Very Unhealthy Days ratio2013": "aqi_bad_2013",
    "Very Unhealthy Days ratio2014": "aqi_bad_2014",
    "Very Unhealthy Days ratio2015": "aqi_bad_2015",
    "Very Unhealthy Days ratio2016": "aqi_bad_2016",
    "Very Unhealthy Days ratio2017": "aqi_bad_2017"
}, inplace = True)

## ===========================================
## save the cleaned air quality data
## ===========================================

df_aqi.to_csv("./aqi_data/aqi_data_clnd.csv")
