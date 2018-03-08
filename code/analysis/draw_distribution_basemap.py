import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize, LogNorm
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import time 
import gc

# http://basemaptutorial.readthedocs.io/en/latest/subplots.html

# https://matplotlib.org/basemap/api/basemap_api.html#mpl_toolkits.basemap.Basemap.drawrivers
# conda install -c conda-forge basemap
# https://matplotlib.org/users/colormapnorms.html
# Source of Georegion: https://www2.census.gov/geo/pdfs/maps-data/maps/reference/us_regdiv.pdf
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

def draw_us_map(map_type, state = None, county_info = None):
    if map_type == "USA":
        # lower left and upper right limits of the bounding box
        # lllon = -119
        lllon = -129
        urlon = - 58
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
    
    if map_type == "county":
        lllon, urlon, lllat, urlat = county_info[0], county_info[1], \
                                     county_info[2], county_info[3]
        
    centerlon = float(lllon + urlon) / 2.0
    centerlat = float(lllat + urlat) / 2.0

    m = Basemap(resolution='i',  # crude, low, intermediate, high, full
                llcrnrlon = lllon, urcrnrlon = urlon,
                lon_0 = centerlon,
                llcrnrlat = lllat, urcrnrlat = urlat,
                lat_0 = centerlat,
                projection = 'cyl')

    return m

def plot_county_choropleth_bystate(varname, state):
	'''
	Plot County Level Choropleth
	'''
	print(state)
	# clean data
	data = pd.read_csv("../../data/database_cleaned.csv", encoding='cp1252')
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
    
def plot_county_choropleth(varname):
    '''
    Plot County Level Choropleth
    '''
    
 	 # clean data
    data = pd.read_csv("../../data/database_cleaned.csv", encoding='cp1252')
    data['COUNTY'] = data['COUNTY'].astype(str)
    data['state'] = data['state'].astype(str)
 
    data.loc[data['COUNTY'].str.len() == 1, 'COUNTY'] = '00' + data.COUNTY
    data.loc[data['COUNTY'].str.len() == 2, 'COUNTY'] = '0' + data.COUNTY
    data.loc[data['state'].str.len() == 1, 'state']  = '0' + data.state

    m = draw_us_map(map_type = "USA")
    fig, ax = plt.subplots(figsize=(10,10))

    m.drawmapboundary(fill_color='#46bcec')
    m.fillcontinents(color='#f2f2f2',lake_color='#46bcec')
    m.drawcoastlines()
    m.readshapefile('../../data/shapefile/US_county/cb_2016_us_county_20m', \
                    'counties', drawbounds = True)

    df_poly = pd.DataFrame({
	        'shapes': [Polygon(np.array(shape), True) for shape in m.counties],
	        'COUNTY': [county['COUNTYFP'] for county in m.counties_info],
	        'state': [county['STATEFP'] for county in m.counties_info]
	    })

    df_poly = df_poly.merge(data, on=['COUNTY', 'state'], how='left')

    #Color scheme from: https://matplotlib.org/examples/color/colormaps_reference.html
    cmap = plt.get_cmap('Oranges')   
    pc = PatchCollection(df_poly.shapes, zorder = 2)
    
    value_min = np.log(df_poly[varname].quantile(q = 0.1))
    value_max = np.log(df_poly[varname].quantile(q = 0.9))

    norm = Normalize()

    pc.set_facecolor(cmap(norm(df_poly[varname].fillna(0).values)))
    ax.add_collection(pc)

    mapper = plt.cm.ScalarMappable(norm=norm, cmap=cmap)

    mapper.set_array(df_poly[varname])

    plt.colorbar(mapper, shrink = 0.3)
    figure_name = "../../output/national_choropleth/national_choropleth" + \
                    varname + ".png"
    fig.savefig(figure_name, bbox_inches='tight', format = 'png', dpi = 300)
    plt.close()   

def plot_county_location(county_FIPS, data):
    '''
    Plot the location of a county
    
    Input:
    - county: (string) County FIPS code
    '''

    fig, ax = plt.subplots(figsize=(10, 10))
    
    m = draw_us_map(map_type = "USA")
    m.drawmapboundary(fill_color = '#46bcec', linewidth = 0.2)
    m.fillcontinents(color = '#FFF8DC',lake_color = '#46bcec')
    m.drawcoastlines(linewidth = 0.2, color = "black")
    m.drawstates(linewidth = 0.2, color = "black")    
    m.readshapefile('../../data/shapefile/US_county/cb_2016_us_county_20m', \
                    'counties', drawbounds = True)

    # Western counties are larger
    if data["Longitude"][county_FIPS] >= 95:
        lllon = - data["Longitude"][county_FIPS] - 2.5       
        urlon = - data["Longitude"][county_FIPS] + 2.5     
        lllat = data["Latitude"][county_FIPS]  - 2.5
        urlat = data["Latitude"][county_FIPS]  + 2.5 
        zoom_time = 2.5
    else:
        lllon = - data["Longitude"][county_FIPS] - 1       
        urlon = - data["Longitude"][county_FIPS] + 1    
        lllat = data["Latitude"][county_FIPS]  - 1
        urlat = data["Latitude"][county_FIPS]  + 1  
        zoom_time = 6

    county_info = (lllon, urlon, lllat, urlat)
    
    axins = zoomed_inset_axes(ax, zoom_time, loc = 4)
    axins.set_xlim(lllon, urlon)
    axins.set_ylim(lllat, urlat)

    plt.xticks(visible = False)
    plt.yticks(visible = False)
    
    map2 = draw_us_map(map_type = "county", county_info = county_info)
    map2.drawmapboundary(fill_color = '#46bcec')
    map2.fillcontinents(color = '#e2e0e0', lake_color='#46bcec')
    map2.drawcountries(linewidth = 0.2)
    map2.drawcoastlines()
    map2.drawrivers(linewidth = 1, linestyle='solid', color = '#46bcec')
    map2.drawstates(linewidth = 2, linestyle='solid', color = 'gray')

    map2.readshapefile('../../data/shapefile/US_county/cb_2016_us_county_20m', \
                   'counties', drawbounds = True)
     
    for i, shape in enumerate(map2.counties):
        county_i_FIPS = map2.counties_info[i]["STATEFP"] + map2.counties_info[i]["COUNTYFP"]
	     
        if county_i_FIPS == county_FIPS:
            color = "red"
        else:
            color = "#FFF8DC"
        poly = Polygon(shape, facecolor = color)
        axins.add_patch(poly)
        
    mark_inset(ax, axins, loc1 = 2, loc2 = 4,  \
               fc = "red", ec = "red", linewidth = 2)
    
    state = str(int(county_FIPS[0:2]))
    county = str(int(county_FIPS[2:]))
    figure_name = "../../output/county_location/county_loc_" + state + "_"+ \
                  county + ".png"
    fig.savefig(figure_name, bbox_inches='tight', format = 'png', dpi = 300)
    plt.close() 
    
    plt.clf()
    del m, map2
    return 0
    
if __name__ == "__main__":

    
    data = pd.read_csv("../../data/database_cleaned.csv")
    
    data['COUNTY'] = data['COUNTY'].astype(str)
    data['state'] = data['state'].astype(str)

    data.loc[data['COUNTY'].str.len() == 1, 'COUNTY'] = '00' + data.COUNTY
    data.loc[data['COUNTY'].str.len() == 2, 'COUNTY'] = '0' + data.COUNTY
    data.loc[data['state'].str.len() == 1, 'state']  = '0' + data.state
    
    data["FIPS"] = data["state"] + data["COUNTY"]
    data = data[['COUNTY', 'state', 'FIPS', 'Longitude', 'Latitude']]
    
    FIPS_list = data['FIPS'].tolist()
    
    data= data.set_index("FIPS")
    
    state_list = ["25", "26", "27", "28", "29", "30", "31", "32", "33", "34", \
                  "35", "36", "37", "38", "39", "40", "41", "42", "44", "45", \
                  "46", "47", "48", "49", "50", "51", "53", "54", "55", "56"]
    
    count = 0
    for FIPS in FIPS_list:
        if FIPS[0:2] in state_list:
            start = time.clock()   
            count += 1
            plot_county_location(FIPS, data)
            print(FIPS, time.clock() - start, count) 
            
            if count == 100:
                gc.collect()
                count = 0
    
    """
    varlist = ["Median_hhinc", "median_rent_value", "median_home_value", \
               "Pov_rate", "Share_college_ormore", "Share_over65", "Share_under18", \
               "crime_rate", "winter_avg_temp", "summer_avg_temp", "annual_avg_temp", \
               "aqi_good"]
    
    for var in varlist:
        plot_county_choropleth(var)
    
    varname = "crime_rate"
    fips_abbr = pd.read_csv("../../data/state_FIPS_abbr.csv", dtype = str)
    
    # for key, item in GEOREGION.items():
    for state in GEOREGION["West"]:
        statecode = fips_abbr.loc[fips_abbr["FIPS"] == state, "abbreviation"].iloc[0]
        plot_county_choropleth_bystate(varname, statecode)
    """