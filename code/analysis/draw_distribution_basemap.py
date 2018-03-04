import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize

# https://www2.census.gov/geo/pdfs/maps-data/maps/reference/us_regdiv.pdf
GEOREGION = {
        "Northeast": ["09", "23", "25", "33", "44", "50", "34", "36", "42"],
        "Midwest": ["18", "17", "26", "39", "55", "19", "20", "27", "29", 
                    "31", "38", "46"],
        "West": ["04", "08", "16", "35", "30", "49", "32", "56", "02", "06",
                 "15", "41", "53"],
        "Southwest": ["05", "22", "40", "48"],
        "Southeast": ["10", "11", "12", "13", "24", "37", "45", "51", "54", 
                      "01", "21", "28", "47"]
        }

def draw_us_map(map_type, state = None):
    if map_type == "USA":
        # lower left and upper right limits of the bounding box
        lllon = -119
        urlon = -64
        lllat = 22.0
        urlat = 50.5
        
        # and calculate a centerpoint, needed for the projection:
        centerlon = float(lllon + urlon) / 2.0
        centerlat = float(lllat + urlat) / 2.0
        
    if map_type == "State":
        data = pd.read_csv("../../data/state_longlat.csv", index_col = "state")
        
        state = state.lower()
        lllon = data["long_range_high"][state] * 1.01
        urlon = data["long_range_low"][state] * 0.99
        lllat = data["lat_range_low"][state] * 0.99
        urlat = data["lat_range_high"][state] * 1.01
        
        print(lllon, urlon, lllat, urlat)
        
        centerlon = float(lllon + urlon) / 2.0
        centerlat = float(lllat + urlat) / 2.0

    m = Basemap(resolution='i',  # crude, low, intermediate, high, full
                llcrnrlon = lllon, urcrnrlon = urlon,
                lon_0 = centerlon,
                llcrnrlat = lllat, urcrnrlat = urlat,
                lat_0 = centerlat,
                projection = 'tmerc')

    return m

def plot_county_choropleth_bystate(datafile, varname, state):
	'''
	Plot County Level Choropleth
	'''
	print(state)
	# clean data
	data = pd.read_csv(datafile)
	data['COUNTY'] = data['COUNTY'].astype(str)
	data['state'] = data['state'].astype(str)

	data.loc[data['COUNTY'].str.len() == 1, 'COUNTY'] = '00' + data.COUNTY
	data.loc[data['COUNTY'].str.len() == 2, 'COUNTY'] = '0' + data.COUNTY
	data.loc[data['state'].str.len() == 1, 'state']  = '0' + data.state

	m = draw_us_map("State", state)
	fig, ax = plt.subplots(figsize=(10,20))

	m.drawmapboundary(fill_color='#46bcec')
	m.fillcontinents(color='#f2f2f2',lake_color='#46bcec')
	m.drawcoastlines()
    
	statecode = fips_abbr.loc[fips_abbr["abbreviation"] == state.upper(), "FIPS"].iloc[0]
	shapefile_path = "../../data/shapefile/US_county_byState/cb_2016_" + \
                     statecode + "_cousub_500k/" + "cb_2016_" + \
                     statecode + "_cousub_500k"
	m.readshapefile(shapefile_path, 'counties', drawbounds = True)

	df_poly = pd.DataFrame({
	        'shapes': [Polygon(np.array(shape), True) for shape in m.counties],
	        'COUNTY': [county['COUNTYFP'] for county in m.counties_info],
	        'state': [county['STATEFP'] for county in m.counties_info]
	    })

	df_poly = df_poly.merge(data, on=['COUNTY', 'state'], how='left')

	cmap = plt.get_cmap('Oranges')   
	pc = PatchCollection(df_poly.shapes, zorder = 2)
	norm = Normalize()

	pc.set_facecolor(cmap(norm(df_poly[varname].fillna(0).values)))
	ax.add_collection(pc)

	mapper = plt.cm.ScalarMappable(norm=norm, cmap=cmap)

	mapper.set_array(df_poly[varname])

	plt.colorbar(mapper, shrink=0.4)
    
	figure_name = "../../output/choropleth/State_choropleth" + state + \
                  varname + ".pdf"
	plt.savefig(figure_name)
    
def plot_region_choropleth(datafile, varname, region):
 	# clean data
	data = pd.read_csv(datafile)
	data['COUNTY'] = data['COUNTY'].astype(str)
	data['state'] = data['state'].astype(str)

	data.loc[data['COUNTY'].str.len() == 1, 'COUNTY'] = '00' + data.COUNTY
	data.loc[data['COUNTY'].str.len() == 2, 'COUNTY'] = '0' + data.COUNTY
	data.loc[data['state'].str.len() == 1, 'state']  = '0' + data.state

	m = draw_us_map()
	fig, ax = plt.subplots(figsize=(10,20))
    
def plot_county_choropleth(datafile, varname):
	'''
	Plot County Level Choropleth
	'''

	# clean data
	data = pd.read_csv(datafile)
	data['COUNTY'] = data['COUNTY'].astype(str)
	data['state'] = data['state'].astype(str)

	data.loc[data['COUNTY'].str.len() == 1, 'COUNTY'] = '00' + data.COUNTY
	data.loc[data['COUNTY'].str.len() == 2, 'COUNTY'] = '0' + data.COUNTY
	data.loc[data['state'].str.len() == 1, 'state']  = '0' + data.state

	m = draw_us_map()
	fig, ax = plt.subplots(figsize=(10,20))

	m.drawmapboundary(fill_color='#46bcec')
	m.fillcontinents(color='#f2f2f2',lake_color='#46bcec')
	m.drawcoastlines()
	m.readshapefile('../../data/shapefile/US_county/cb_2016_us_county_500k', \
                    'counties', drawbounds=True)

	df_poly = pd.DataFrame({
	        'shapes': [Polygon(np.array(shape), True) for shape in m.counties],
	        'COUNTY': [county['COUNTYFP'] for county in m.counties_info],
	        'state': [county['STATEFP'] for county in m.counties_info]
	    })

	df_poly = df_poly.merge(data, on=['COUNTY', 'state'], how='left')

	cmap = plt.get_cmap('Oranges')   
	pc = PatchCollection(df_poly.shapes, zorder = 2)
	norm = Normalize()

	pc.set_facecolor(cmap(norm(df_poly[varname].fillna(0).values)))
	ax.add_collection(pc)

	mapper = plt.cm.ScalarMappable(norm=norm, cmap=cmap)

	mapper.set_array(df_poly[varname])

	plt.colorbar(mapper, shrink=0.4)
	plt.show()

if __name__ == "__main__":
    filename = "../../data/ACS_data.txt"

	# Sample call of the function
    varname = "Median_hhinc"
    # plot_county_choropleth(filename, varname)
    fips_abbr = pd.read_csv("../../data/state_FIPS_abbr.csv", dtype = str)
    
    for key, item in GEOREGION.items():
        for state in item:
            statecode = fips_abbr.loc[fips_abbr["FIPS"] == state, "abbreviation"].iloc[0]
            plot_county_choropleth_bystate(filename, varname, statecode)