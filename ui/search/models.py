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
from itertools import combinations


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
lst_to_valid1 = [    # list of vars with one argument
                "Region",
                "State_name",
				]

lst_to_valid2 = [    # list of vars with two bounding arguments
                "winter_avg_temp",
                "summer_avg_temp",
                "Median_hhinc", 
                "median_rent_value", 
                "median_home_value", 
                ]
lst_to_valid3 = [    # list of vars with percentage range
                "Share_college_ormore",
                "Share_over65",
                ]

lst_to_valid4 = [    # list of vars with only one bounding args
                "aqi_good"
            	]

lst_to_valid5 = [    # list of vars with multiple choices
                "largest_race"
	            ]

class county_profile():
	'''
	THis is the class to provide simple profile information of counties, majorly for
	presentation of recommended counties in recommended counties' list that
	will be shown in the main page recommended counties list and the 
	similar counties search engine in the county detail webpage
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

	if len(args.keys()) == 0:    # case where no user input is given
		return

	NUM_ROW = df.shape[0]
	filter_ = pd.Series([True] * NUM_ROW )   # initialize the filter
	## =====================================================
	## Main idea is to go through all different user input 
	## stored in the args and update the filter_ along the 
	## way and in the end used the most updated filter
	## to filter the data frame to generate the list of 
	## recommended counties
	## =====================================================

	for key, bnds in args.items():

		if key in lst_to_valid1:
			## this is the case where we only have one certain user input
			## e.g., Region or State 

			filter_ = (filter_) & ( df[key] ==  bnds)
		
		elif key == "largest_race":
			## we single out the largest race becasue it actually 
			## means whether certain counties' largest racical composition 
			## is in user's list of largest racial composition

			filter_ = (filter_) & pd.Series(
					[i in bnds for i in df[key]]
				)
		else:
			## case where we have both lower bound and upper bound

			lb, ub  = bnds
			filter_ = (filter_) & (df[key] >= lb) & (df[key] <= ub)

	## filtering the df using the updated filter
	df_filtered = df[filter_]

	## prepare the result
	## For easiness of passing the recommended counties to the html
	## we design the recommended counties to be a county_profile object

	recommendation = [
		county_profile(row["NAME"], row["ST"], row["COUNTY"], row["State_name"]) 
		for i, row in df_filtered.iterrows()
	]

	return recommendation


def relax_input(df, args):
	'''
	This function will provide user with hints on which inputs to relax when 
	there is no matched counties based on their original query

	'''

	## the following rename dictionary is purely for user-friendly design to 
	## convert the varaible name in our database to user-readable names to 
	## guide them how to refine their input
	rename = {
		"Region": "Region",
		"State_name": "State",
		"winter_avg_temp": "lowest winter average",
		"summer_avg_temp": "highest summer average",
		"Share_over65": "Share of residents over 65",
		"aqi_good": "Air quality",
		"largest_race": "Largest race composition",
		"Median_hhinc": "Median household income",
		"median_rent_value": "Median rent",
		"median_home_value": "Median house value",
		"Share_college_ormore": "Share of residents with higher education"

	}

	keys_list = []    # initialize the keys list to store inputs suggested to relax
	num_keys = len(args.keys())

	for i in range(num_keys):
		num = i + 1
		var_to_del = list(combinations(list(args.keys()), num))
		for var in var_to_del:
			var_list = list(var)
			var_name = tuple([rename[v] for v in var_list])
			new_args = dict((k, args[k]) for k in args.keys() if k not in var_list)
			if find_counties(df, new_args) is not None and \
			len(find_counties(df, new_args)) > 0:
				keys_list.append(var_name)   # if the subset of a user input dictionary
											 # will generate recommended counties
											 # we will record the set of inputs to relax

	return keys_list



class county_detail():
	'''
	This class will be used to display all kinds of details and visualizations 
	of the recommended counties.
	'''
	def __init__(self, ST, COUNTY, df):
		self.ST = int(ST)
		self.COUNTY = int(COUNTY)
		self.df = df    # load in the database
		self.row = self._get_row_()    # get the row corresponds to recommended county
		self.name = self.row['NAME']   # county name
		self.pop = self.row.Population
		self.share_over65 = "{0:.2f}%".format(self.row.Share_over65 * 100)
		self.share_college_ormore = "{0:.2f}%".format(
			self.row.Share_college_ormore * 100)
		self.share_highschool_orless = "{0:.2f}%".format(
			self.row.Share_highschool_orless * 100)
		self.median_home_value = "{:d}".format(int(self.row.median_home_value))
		self.median_rent_value = "${:d}".format(int(self.row.median_rent_value) )
		self.airport = {"airport": self.row.airport, 
			"dist": "{:d} km away".format(int(self.row.dist_airport))}
		self.pov_rate = "{0:.2f}%".format(self.row.Pov_rate * 100)
		self.unemp_rate = "{0:.2f}%".format(self.row.unemp_rate * 100)
		self.crime_rate = "{0:.2f}%".format(self.row.crime_rate * 100)
		self.Median_hhinc = "${:d}".format(int(self.row.Median_hhinc))


	def _get_row_(self):
		'''
		This method will return the row of the identified county in the database
		This method is "private" in the sense that will only be called within the 
		constructor of county_detail class.
		Return:
			row: (A pandas Series)

		'''
		row = self.df.loc[(self.df.ST == self.ST) & 
			(self.df.COUNTY == self.COUNTY)]

		return row.iloc[0]


	def temperature_viz(self):
		'''
		This method will visualize the temperature and precipitation over 12 months
		for the recommended county.

		'''
		filename = "{}/static/temp_viz.png".format(settings.BASE_DIR)
		if os.path.exists(filename):
			os.remove(filename)
		var_list_avg_temp = [v+"_avg_temp" for v in month_lst]
		var_list_max_temp = [v+"_max_temp" for v in month_lst]
		var_list_min_temp = [v+"_min_temp" for v in month_lst]
		var_list_prcp = [v+"_prcp" for v in month_lst]
		avg_temp = self.row.loc[var_list_avg_temp].values
		max_temp = self.row.loc[var_list_max_temp].values
		min_temp = self.row.loc[var_list_min_temp].values
		prcp = self.row.loc[var_list_prcp].values
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


	def racial_distribution(self):
		'''
		This method will plot the racial distribution of the recommended county
		'''
		filename = "{}/static/racial_distribution.png".format(settings.BASE_DIR)
		if os.path.exists(filename):
			os.remove(filename)
		race_list = ["Hispanic_Latino", "White", "Black", "Asian"]
		race_index = np.arange(len(race_list))
		race_share = self.row[race_list].values * 100
		plt.figure(figsize = (8, 5))
		plt.bar(race_index, race_share, align = "center", color = "orange", alpha = 0.3)
		plt.xticks(race_index, race_list)
		plt.ylabel("Share (percentage)")
		plt.suptitle("Racial distribution", fontsize = 25)

		plt.savefig(filename)
		plt.close()

	
	def find_similar_counties(self, args):
		#row = self._get_row_()
		cols = args["var_of_interest"]
		current = self.row[cols].values
		lst = [self.df[cols].iloc[i].values 
			for i in range(self.df.shape[0])]

		nn = NearestNeighbors(algorithm = "kd_tree")
		nn.fit(lst)
		nn_ind = nn.kneighbors([current], 6, False)[0]
		nn_ind = nn_ind[1:]
		recommendation = [
			county_profile(row["NAME"], row["ST"], row["COUNTY"], row["State_name"]) 
			for i, row in self.df.iloc[nn_ind].iterrows()
		]
		return recommendation
		
		
	

'''
## ===============================================================
## Below are just some obsolete code to construct the Kd-tree
## for nearest neighbor algorithm, which is replaced by the simple 
## sckitlearn-package later on
## These code are from 
## ===============================================================


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
    axis = depth 
 
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
    axis = depth 
 
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
