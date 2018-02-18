import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize

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
    plot_county_choropleth(filename, varname)