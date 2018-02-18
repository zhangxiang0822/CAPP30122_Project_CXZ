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
	data.to_csv(filename, sep=',', encoding = 'utf-8')

if __name__ == "__main__":
	filename = "../../data/ACS_data.txt"
	query_data(filename)
