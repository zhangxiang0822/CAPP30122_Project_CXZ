from bs4 import BeautifulSoup
import urllib.request
import requests
import zipfile
import re


url = "aqs.epa.gov/aqsweb/airdata/download_files.html#AQI"
file_prefix = "annual_aqi_by_county_"
download_prefix = "https://aqs.epa.gov/aqsweb/airdata/"
download_dir = "./download_zips/"
data_dir = "./aqi_data/"

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

