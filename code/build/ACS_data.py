import requests
import pandas as pd

def generate_newvars(data):
    '''
    After getting data, generate new variables using existing variables.
    The generated new variables are:
        - Sex_ratio
    '''
        
    data['Pov_rate'] = data['Num_in_pov'] / data['Num_pov_det']
    
    return data

def query_population_data():
    '''
    This function queries information on population
    '''
    varlist = [
				"COUNTY", 
				"NAME", 
				"ST", 
                "B01001_003E",  # Male under 5
				"B01001_004E",  # Male 5 - 9
                "B01001_005E",  # Male 10 - 14
                "B01001_006E",  # Male 15 - 17 
                "B01001_007E",  # Male 18 - 19
                "B01001_008E",  # Male 20
                "B01001_009E",  # Male 21
                "B01001_010E",  # Male 22 - 24
                "B01001_011E",  # Male 25 - 29
                "B01001_012E",  # Male 30 - 34
                "B01001_013E",  # Male 35 - 39
                "B01001_014E",  # Male 40 - 44
                "B01001_015E",  # Male 45 - 49
                "B01001_016E",  # Male 50 - 54
                "B01001_017E",  # Male 55 - 59
                "B01001_018E",  # Male 60 - 61
                "B01001_019E",  # Male 62 - 64
                "B01001_020E",  # Male 65 - 66
                "B01001_021E",  # Male 67 - 69
                "B01001_022E",  # Male 70 - 74
                "B01001_023E",  # Male 75 - 79
                "B01001_024E",  # Male 80 - 84
                "B01001_025E",  # Male 85+
                "B01001_027E",  # Female under 5
				"B01001_028E",  # Female 5 - 9
                "B01001_029E",  # Female 10 - 14
                "B01001_030E",  # Female 15 - 17 
                "B01001_031E",  # Female 18 - 19
                "B01001_032E",  # Female 20
                "B01001_033E",  # Female 21
                "B01001_034E",  # Female 22 - 24
                "B01001_035E",  # Female 25 - 29
                "B01001_036E",  # Female 30 - 34
                "B01001_037E",  # Female 35 - 39
                "B01001_038E",  # Female 40 - 44
                "B01001_039E",  # Female 45 - 49
                "B01001_040E",  # Female 50 - 54
                "B01001_041E",  # Female 55 - 59
                "B01001_042E",  # Female 60 - 61
                "B01001_043E",  # Female 62 - 64
                "B01001_044E",  # Female 65 - 66
                "B01001_045E",  # Female 67 - 69
                "B01001_046E",  # Female 70 - 74
                "B01001_047E",  # Female 75 - 79
                "B01001_048E",  # Female 80 - 84
                "B01001_049E",  # Female 85+
				]
    
    varstring = "?get=" + ",".join(varlist) + "&for=county:*"

    query_request = "https://api.census.gov/data/2015/acs5" + varstring
    print(query_request)

    r = requests.get(query_request)
    pop_data_json = r.json()
    
    pop_data = pd.DataFrame(pop_data_json[1:], columns = pop_data_json[0])
    
    for var in varlist[3:]:
        pop_data[var] = pd.to_numeric(pop_data[var])
        
    age_under18_vars = ['B01001_003E', 'B01001_004E', 'B01001_005E', 'B01001_006E', \
                        'B01001_027E', 'B01001_028E', 'B01001_029E', 'B01001_030E']
    age_over65_vars  = ['B01001_020E', 'B01001_021E', 'B01001_022E', 'B01001_023E', \
                        'B01001_024E', 'B01001_025E', 'B01001_044E', 'B01001_045E', \
                        'B01001_046E', 'B01001_047E', 'B01001_048E', 'B01001_049E']
    pop_data['Pop_under18'] = pop_data[age_under18_vars].sum(axis = 1)
    pop_data['Pop_over65']  = pop_data[age_over65_vars].sum(axis = 1)
    pop_data['Population1'] = pop_data.sum(axis = 1)
    
    return_var_list = ['COUNTY', 'ST', 'Pop_under18', 'Pop_over65']
    
    pop_data = pop_data[return_var_list]
    return pop_data
    
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
    B08201_001E: Household size
    B15002_001E: Age 25 or over (serve as the universe for tabulating educational attainment)
    B17001_001E: Number of persons for whom poverty status is determined
    B17001_002E: Number of persons in poverty
    B19013_001E: Median household income (in 2015 USD)
    B19301_001E: Per capita income (in 2015 USD)
    B25058_001E: Median rent value
    B25077_001E: Median home value 
	'''
	## Generate query
	varlist = [
				"COUNTY", 
				"NAME", 
				"ST", 
                "B00001_001E",
				"B00002_001E",
				"B08201_001E",
                "B15002_001E", 
                "B17001_001E",
                "B17001_002E",
                "B19013_001E",
                "B19301_001E", 
                "B25058_001E",
                "B25077_001E"
				]

	varstring = "?get=" + ",".join(varlist) + "&for=county:*"

	query_request = "https://api.census.gov/data/2015/acs5" + varstring
	print(query_request)

	r = requests.get(query_request)
	acs_data = r.json()
	varname_list = ['COUNTY', 'NAME', 'ST', 'Population', \
                    'Num_household',  \
                    'Household_size', 'Age25_over', \
                    'Num_pov_det', 'Num_in_pov', \
                    'Median_hhinc', 'Incpc', \
                    'median_rent_value', 'median_home_value', \
                    'state', 'county']

	# Fron nexted list to pandas dataframe
	data = pd.DataFrame(acs_data[1:], columns = varname_list)

	numeric_varlist = ['Population', 'Num_household', \
                       'Household_size', 'Age25_over', \
                       'Num_pov_det', 'Num_in_pov', \
                       'median_rent_value', 'median_home_value', \
                       'Median_hhinc', 'Incpc']
	for var in numeric_varlist:
		data[var] = pd.to_numeric(data[var])
		print(var, data[var].mean())

	data = generate_newvars(data)
	pop_data = query_population_data()
    
	data = data.merge(pop_data, on = ['COUNTY', 'ST'])
	data.to_csv(filename, sep=',', encoding = 'utf-8')

if __name__ == "__main__":
	filename = "../../data/ACS_data.txt"
	query_data(filename)
