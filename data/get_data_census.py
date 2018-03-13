import requests
import pandas as pd

'''
Note: This Python code file is used to access data using Census bureau's API
The variables get include:
    - Social Demographic variable
    - Population
    
Using these variables, I generate:
    - Race composition variables
'''

def generate_newvars(data):
    '''
    After getting data, generate new variables using existing variables.
    The generated new variables are:
        - Hispanic_Latino_share
        - White_share
        - Black_share
        - Asian_share
        
    Input:
        - data: (pandas dataframe)
        
    Return:
        - data: (pandas dataframe) after generating new variables
    '''
                    
    data['Hispanic_Latino_share'] = data['Hispanic_Latino'] / data['Population']
    data['White_share'] = data['White'] / data['Population']
    data['Black_share'] = data['Black'] / data['Population']
    data['Asian_share'] = data['Asian'] / data['Population']
    
    return data

def query_data(filename):
	'''
	Query data using Census bureau API and save the data
    Census data Variable list: https://api.census.gov/data/2015/acs5/variables.html

    Note: The API user_key used to access census bureau data is for my own use,
    and are provided here just in order to make sure you can smoothly run the code,
    please don't share it with others
    
    Input:
        - filename: (string) The output filename
        
    Returns:
        - No returns
    
    Output:
        - csv file named filename
	'''
    
	## Generate query
	varlist = [
				"P0090001", # Total population
                "P0090002", # Hispanic or Latino population
                "P0090005", # White alone
                "P0090006", # Black or African American alone
                "P0090008", # Asian
                "H0020002"  # Urban
				]

	user_key = "996f6db272b0617e29bf54610959a45b94de221f"
	varstring = "?get=" + ",".join(varlist) + ",NAME&for=county:*&key=" + user_key

	query_request = "https://api.census.gov/data/2010/sf1" + varstring

	r = requests.get(query_request)
	census_data = r.json()

	varname_list = ['Population',  \
                    'Hispanic_Latino', \
                    'White', \
                    'Black', \
                    'Asian', \
                    'Urban', \
                    'NAME', 'state', 'county']
    
	# Fron nested list to pandas dataframe
	data = pd.DataFrame(census_data[1:], columns = varname_list)
    
	numeric_varlist = ['Population', "White", 'Hispanic_Latino', 'Black', \
                       'Asian', 'Urban']

	for var in numeric_varlist:
		data[var] = pd.to_numeric(data[var])

	data = generate_newvars(data)

	data.to_csv(filename, sep=',', encoding = 'utf-8')
    
if __name__ == "__main__":
	filename = "../../data/census_data.txt"
	query_data(filename)