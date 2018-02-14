from census import Census
from us import states
import requests
import json
import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


def query_data(filename):
	'''
	send query to Census bureau API and save the data
    Census data Variable list: https://api.census.gov/data/2015/acs5/variables.html
    
    Code reference: http://shallowsky.com/blog/programming/plotting-election-data-basemap.html
                    https://github.com/akkana/scripts/blob/master/mapping/election2016/bluered-censusshapes.py
                    https://github.com/jamalmoir/notebook_playground/blob/master/uk_2015_houseprice.ipynb

    COUNTY: FIPS County code
    NAME: Geographic Area Name
    ST: State FIPS code
    B00001_001E: Total population
    B00002_001E: Total number of households
    B01001_001E: Sex by age (total)
    B10058_002E: In labor force
    B08201_001E: Household size
	'''
	## Generate query
	varlist = [
				"COUNTY", 
				"NAME", 
				"ST", 
				"B00001_001E",
				"B00002_001E",
				"B01001_001E",
				"B10058_002E",
				"B08201_001E"
				]

	varstring = "?get=" + ",".join(varlist) + "&for=county:*"

	query_request = "https://api.census.gov/data/2015/acs5" + varstring
	print(query_request)

	r = requests.get(query_request)
	acs_data = r.json()
	varname_list = ['COUNTY', 'NAME', 'ST', 'Population', 'Sex', 'Num_household', 'Employed', \
                    'Household_size', 'state', 'county']

	# Fron nexted list to pandas dataframe
	data = pd.DataFrame(acs_data[1:], columns = varname_list)

	numeric_varlist = ['Population', 'Sex', 'Num_household', 'Employed', 'Household_size']
	for var in numeric_varlist:
		data[var] = pd.to_numeric(data[var])
   
	data.to_csv(filename, sep=',', encoding = 'utf-8')

def draw_us_map():
    # Set the lower left and upper right limits of the bounding box:
    lllon = -119
    urlon = -64
    lllat = 22.0
    urlat = 50.5
    # and calculate a centerpoint, needed for the projection:
    centerlon = float(lllon + urlon) / 2.0
    centerlat = float(lllat + urlat) / 2.0

    m = Basemap(resolution='i',  # crude, low, intermediate, high, full
                llcrnrlon = lllon, urcrnrlon = urlon,
                lon_0 = centerlon,
                llcrnrlat = lllat, urcrnrlat = urlat,
                lat_0 = centerlat,
                projection='tmerc')

    return m

def plot_county_choropleth(datafile):
	'''
	Plot County Level Choropleth
	'''
	data = pd.read_csv(datafile)

	fig, ax = plt.subplots(figsize=(10,20))

	m.drawmapboundary(fill_color='#46bcec')
	m.fillcontinents(color='#f2f2f2',lake_color='#46bcec')
	m.drawcoastlines()
	m.readshapefile('cb_2016_us_county_500k', 'counties', drawbounds=True)

	df_poly = pd.DataFrame({
	        'shapes': [Polygon(np.array(shape), True) for shape in m.counties],
	        'COUNTY': [county['COUNTYFP'] for county in m.counties_info],
	        'state': [county['STATEFP'] for county in m.counties_info]
	    })

	df_poly = df_poly.merge(data, on=['COUNTY', 'state'], how='left')

	cmap = plt.get_cmap('Oranges')   
	pc = PatchCollection(df_poly.shapes, zorder = 2)
	norm = Normalize()

	pc.set_facecolor(cmap(norm(df_poly['Sex_ratio'].fillna(0).values)))
	ax.add_collection(pc)

	mapper = plt.cm.ScalarMappable(norm=norm, cmap=cmap)

	mapper.set_array(df_poly['Sex_ratio'])

	plt.colorbar(mapper, shrink=0.4)
	plt.show()

if __name__ == "__main__":
	filename = "ACS_data.txt"
    query_data(filenmae)
    plot_county_choropleth(filenmae)
