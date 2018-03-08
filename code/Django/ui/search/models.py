import os
from django.db import models
import pandas as pd
import matplotlib.pyplot as plt
#import Image
from django.conf import settings
import pandas as pd
import numpy as np
#from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize

from collections import namedtuple
from operator import itemgetter
from pprint import pformat

from sklearn.neighbors import NearestNeighbors


month_lst = ["Jan",
			 "Feb",
			 "Mar",
			 "Apr",
			 "May",
			 "Jun",
			 "Jul",
			 "Aug",
			 "Sep",
			 "Oct",
			 "Nov",
			 "Dec"]
lst_to_valid1 = [    # list with one argument
                "Region",
                "State_name",
                #"largest_race",
            ]
lst_to_valid2 = [
                
                "winter_avg_temp",
                "summer_avg_temp",
                #"unemp_rate",
                #"Share_over65",
                #"Share_under18",
                #"Share_college_ormore",

                #"Population",
                #"Num_household",
                "Median_hhinc", 
                "Incpc",
                "median_rent_value", 
                "median_home_value", 
                #"Pov_rate" ,
                #"aqi_good", 
                #"aqi_bad", 
                #"crime_rate"
                ]
lst_to_valid3 = [
                #"aqi_good",
                "unemp_rate",
                "Pov_rate",
                "Share_college_ormore",
                "Share_over65",
                #"Share_under18",

            ]

lst_to_valid4 = [
                "aqi_good"
            ]
lst_to_valid5 = [
				"largest_race"
]

class county_profile():
	'''
	THis is the class to provide simple profil information of counties, majorly for
	presentation of recommended counties in recommended counties' list
	'''
	def __init__(self, NAME, ST, COUNTY, State_name):
		self.NAME = NAME
		self.ST = ST
		self.COUNTY = COUNTY
		self.State_name = State_name



def find_counties(df, args):
	'''
	This function will take a database(pandas dataframe) and an query arguments
	(dictionary) and return the result in the form of:
	( a list of strings(column names), a list of tuples  )
	'''
	## importing the database

	if len(args.keys()) == 0:
		return[[], []]
	NUM_ROW = df.shape[0]
	filter_ = pd.Series([True] * NUM_ROW )   # initialize the filter
	for key, bnds in args.items():

		if key in lst_to_valid1:
			filter_ = (filter_) & ( df[key] ==  bnds)
		elif key == "largest_race":
			filter_ = (filter_) & pd.Series(
					[i in bnds for i in df[key]]
				)
		else:
			lb, ub  = bnds
			filter_ = (filter_) & (df[key] >= lb) & (df[key] <= ub)

	## filtering the df
	df_filtered = df[filter_]

	## prepare the result
	#columns = ["County Name", "State FIPS", "County FIPS"]
	recommendation = [
		county_profile(row["NAME"], row["ST"], row["COUNTY"], row["State_name"]) 
		for i, row in df_filtered.iterrows()
	]


	return recommendation



class county_detail():
	'''
	This class will be used to display all kinds of details and visualizations 
	of the recommended counties.
	'''
	def __init__(self, ST, COUNTY):
		#self.NAME = NAME
		self.ST = int(ST)
		self.COUNTY = int(COUNTY)


	def get_row(self, df):
		'''
		This method will return the row of the identified county in the database
		Return:
			row: (A pandas Series)

		'''
		row = df.loc[(df.ST == self.ST) & (df.COUNTY == self.COUNTY)]

		return row.iloc[0]



	def get_name(self, df):

		return self.get_row(df)["NAME"]

	'''
	def aqi(self, df):
		
		YEARS = [2013, 2014, 2015, 2016, 2017]
		row = self.get_row(df)
		aqi_table = [ (YEAR,
					   row["aqi_good_" + str(YEAR) ],
					   row["aqi_bad_" + str(YEAR) ]) for YEAR in YEARS]
		aqi_table_column = ["Year", 
							"Percentage of days classified as 'GOOD'",
							"Percentage of days classified as 'VERY UNHEALTHY"]

		return (aqi_table_column, aqi_table)
	'''


	def pop(self, df):
		row = self.get_row(df)
		return row.Population

	def share_over65(self, df):
		row = self.get_row(df)
		return "{0:.2f}%".format(row.Share_over65 * 100)

	def share_college_ormore(self, df):
		row = self.get_row(df)
		return "{0:.2f}%".format(row.Share_college_ormore * 100)

	def share_highschool_orless(self, df):
		row = self.get_row(df)
		return "{0:.2f}%".format(row.Share_highschool_orless * 100)

	def median_home_value(self, df):
		row = self.get_row(df)
		return "{:d}".format(int(row.median_home_value) )

	def median_rent_value(self, df):
		row = self.get_row(df)
		return "${:d}".format(int(row.median_rent_value) )

	
	def airport(self, df):
		row = self.get_row(df)
		return {"airport": row.airport, 
			"dist": "{:d} km away".format(int(row.dist_airport))}

	def pov_rate(self, df):
		row = self.get_row(df)
		return "{0:.2f}%".format(row.Pov_rate * 100)


	def unemp_rate(self, df):
		row = self.get_row(df)
		return "{0:.2f}%".format(row.unemp_rate * 100)


	def crime_rate(self, df):
		row = self.get_row(df)
		return "{0:.2f}%".format(row.crime_rate * 100)



	def temperature_viz(self, df):
		row = self.get_row(df)
		#filename = "{}/static/{}-{}.png".format(settings.BASE_DIR, self.ST, self.COUNTY)
		filename = "{}/static/temp_viz.png".format(settings.BASE_DIR)
		if os.path.exists(filename):
			os.remove(filename)
		var_list_avg_temp = [v+"_avg_temp" for v in month_lst]
		var_list_max_temp = [v+"_max_temp" for v in month_lst]
		var_list_min_temp = [v+"_min_temp" for v in month_lst]
		var_list_prcp = [v+"_prcp" for v in month_lst]
		avg_temp = row.loc[var_list_avg_temp].values
		max_temp = row.loc[var_list_max_temp].values
		min_temp = row.loc[var_list_min_temp].values
		prcp = row.loc[var_list_prcp].values
		df_temp = pd.DataFrame({
			"avg_temp": avg_temp,
			"max_temp": max_temp,
			"min_temp": min_temp,
			"precipitation": prcp
			})
		fig, ax1 = plt.subplots(figsize=(8, 5))
		ax2 = ax1.twinx()
		df_temp['avg_temp'].plot(kind='line',marker='d', 
										 color = "orange", ax=ax1, zorder = 2, 
										 label = "Average temperature")
		#df_temp["max_temp"].plot(kind='line', linestyle = ":",
		#						color = "y", marker='d', ax=ax1, zorder = 3, 
		#								 label = "Maximum temperature")
		#df_temp["min_temp"].plot(kind='line', linestyle = ":",
		#						color = "m", marker='d', ax=ax1, zorder = 4, 
		#								 label = "Minimum temperature")		
		df_temp["precipitation"].plot(kind='bar', color='orange', ax=ax2, alpha= 0.3,
									  zorder = 1, 
										 label = "Precipitation")
		ax1.legend(loc= "upper right")
		ax2.legend(loc= "upper left")

		ax1.set_ylabel("Temperature (Fahrenheit)")
		ax2.set_ylabel("Precipitation (mm)")
		ax1.set_xlabel("Month")
		plt.xticks(range(12), month_lst)

		ax1.yaxis.tick_left()
		ax2.yaxis.tick_right()
		plt.suptitle("Weather summary", fontsize = 25)


		plt.savefig(filename)
		plt.close()


	def racial_distribution(self, df):
		row = self.get_row(df)
		#filename = "{}/static/{}-{}.png".format(settings.BASE_DIR, self.ST, self.COUNTY)
		filename = "{}/static/racial_distribution.png".format(settings.BASE_DIR)
		if os.path.exists(filename):
			os.remove(filename)
		race_list = ["Hispanic_Latino", "White", "Black", "Asian"]
		race_index = np.arange(len(race_list))
		race_share = row[race_list].values * 100
		plt.figure(figsize = (8, 5))
		plt.bar(race_index, race_share, align = "center", color = "orange", alpha = 0.3)
		plt.xticks(race_index, race_list)
		plt.ylabel("Share (percentage)")
		plt.suptitle("Racial distribution", fontsize = 25)

		plt.savefig(filename)
		plt.close()

	
	def find_similar_counties(self, df, args):
		row = self.get_row(df)
		cols = args["var_of_interest"]
		current = row[cols].values
		lst = [df[cols].iloc[i].values 
			for i in range(df.shape[0])]

		nn = NearestNeighbors(algorithm = "kd_tree")
		nn.fit(lst)
		nn_ind = nn.kneighbors([current], 5, False)[0]
		recommendation = [
			county_profile(row["NAME"], row["ST"], row["COUNTY"], row["State_name"]) 
			for i, row in df.iloc[nn_ind].iterrows()
		]

		'''
		## geographically close
		current_geo_loc = [row.Latitude, row.Longitude]
		geo_loc_list = [[df.iloc[i].Latitude, df.iloc[i].Longitude] 
			for i in range(df.shape[0])]

		geo_nn = NearestNeighbors(algorithm = "kd_tree")
		geo_nn.fit(geo_loc_list)
		geo_nn_ind = geo_nn.kneighbors([current_geo_loc], 5, False)[0]
		geo_recommendation = [
			county_profile(row["NAME"], row["ST"], row["COUNTY"], row["State_name"]) 
			for i, row in df.iloc[geo_nn_ind].iterrows()
		]
		## weather
		current_weather = [row.winter_avg_temp, row.summer_avg_temp]
		weather_list = [[df.iloc[i].winter_avg_temp, df.iloc[i].summer_avg_temp] 
			for i in range(df.shape[0])]

		weather_nn = NearestNeighbors(algorithm = "kd_tree")
		weather_nn.fit(weather_list)
		weather_nn_ind = weather_nn.kneighbors([current_weather], 5, False)[0]
		weather_recommendation = [
			county_profile(row["NAME"], row["ST"], row["COUNTY"], row["State_name"]) 
			for i, row in df.iloc[weather_nn_ind].iterrows()
		]
		'''
		
		return recommendation
	

'''
class Node(namedtuple('Node', 'location left_child right_child')):
 
    def __repr__(self):
        return pformat(tuple(self))
 
def kdtree(point_list, depth=0):
    """ build K-D tree
    :param point_list list of input points
    :param depth      current tree's depth
    :return tree node
    """
 
    # assumes all points have the same dimension
    try:
        k = len(point_list[0])
    except IndexError:
        return None
 
    # Select axis based on depth so that axis cycles through
    # all valid values
    axis = depth % k
 
    # Sort point list and choose median as pivot element
    point_list.sort(key=itemgetter(axis))
    median = len(point_list) // 2         # choose median
 
    # Create node and construct subtrees
    return Node(
        location=point_list[median],
        left_child=kdtree(point_list[:median], depth + 1),
        right_child=kdtree(point_list[median + 1:], depth + 1)
    )

nearest_nn = None           # nearest neighbor (NN)
distance_nn = float('inf')  # distance from NN to target
 
def nearest_neighbor_search(tree, target_point, hr, distance, nearest=None, depth=0):
    """ Find the nearest neighbor for the given point (claims O(log(n)) complexity)
    :param tree         K-D tree
    :param target_point given point for the NN search
    :param hr           splitting hyperplane
    :param distance     minimal distance
    :param nearest      nearest point
    :param depth        tree's depth
    """
 
    global nearest_nn
    global distance_nn
 
    if tree is None:
        return
 
    k = len(target_point)
 
    cur_node = tree.location         # current tree's node
    left_branch = tree.left_child    # its left branch
    right_branch = tree.right_child  # its right branch
 
    nearer_kd = further_kd = None
    nearer_hr = further_hr = None
    left_hr = right_hr = None
 
    # Select axis based on depth so that axis cycles through all valid values
    axis = depth % k
 
    # split the hyperplane depending on the axis
    if axis == 0:
        left_hr = [hr[0], (cur_node[0], hr[1][1])]
        right_hr = [(cur_node[0],hr[0][1]), hr[1]]
 
    if axis == 1:
        left_hr = [(hr[0][0], cur_node[1]), hr[1]]
        right_hr = [hr[0], (hr[1][0], cur_node[1])]
 
    # check which hyperplane the target point belongs to
    if target_point[axis] <= cur_node[axis]:
        nearer_kd = left_branch
        further_kd = right_branch
        nearer_hr = left_hr
        further_hr = right_hr
 
    if target_point[axis] > cur_node[axis]:
        nearer_kd = right_branch
        further_kd = left_branch
        nearer_hr = right_hr
        further_hr = left_hr
 
    # check whether the current node is closer
    dist = (cur_node[0] - target_point[0])**2 + (cur_node[1] - target_point[1])**2
 
    if dist < distance:
        nearest = cur_node
        distance = dist
 
    # go deeper in the tree
    nearest_neighbor_search(nearer_kd, target_point, nearer_hr, distance, nearest, depth+1)
 
    # once we reached the leaf node we check whether there are closer points
    # inside the hypersphere
    if distance < distance_nn:
        nearest_nn = nearest
        distance_nn = distance
 
    # a nearer point (px,py) could only be in further_kd (further_hr) -> explore it
    px = compute_closest_coordinate(target_point[0], further_hr[0][0], further_hr[1][0])
    py = compute_closest_coordinate(target_point[1], further_hr[1][1], further_hr[0][1])
 
    # check whether it is closer than the current nearest neighbor => whether a hypersphere crosses the hyperplane
    dist = (px - target_point[0])**2 + (py - target_point[1])**2
 
    # explore the further kd-tree / hyperplane if necessary
    if dist < distance_nn:
        nearest_neighbor_search(further_kd, target_point, further_hr, distance, nearest, depth+1)


def compute_closest_coordinate(value, range_min, range_max):
    """ Compute the closest coordinate for the neighboring hyperplane
    :param value     coordinate value (x or y) of the target point
    :param range_min minimal coordinate (x or y) of the neighboring hyperplane
    :param range_max maximal coordinate (x or y) of the neighboring hyperplane
    :return x or y coordinate
    """
 
    v = None
 
    if range_min < value < range_max:
        v = value
 
    elif value <= range_min:
        v = range_min
 
    elif value >= range_max:
        v = range_max
 
    return v

'''