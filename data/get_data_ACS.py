import requests
import pandas as pd

'''
Note: This Python code file is used to access data using Census bureau's API
'''

def generate_newvars(data):
    '''
    After getting data, generate new variables using existing variables.
    The generated new variables are:
        - Poverty rate
        - Share of people with high school degree or less
        - Share of people with college degree or more
        
    Input:
        - data: (pandas dataframe)
        
    Return:
        - data: (pandas dataframe) after generating new variables
    '''
        
    data['Pov_rate'] = data['Num_in_pov'] / data['Num_pov_det']
    data['Share_highschool_orless'] = data['High_school_orless'] / data['Pop_over25']
    data['Share_college_ormore'] = data['College_ormore'] / data['Pop_over25']
    
    return data

def request_data(varlist):
    '''
    Given a variable list, request data from that url
    
    Input:
        - varlist: (list) list of variables to be queried
    
    Return:
        - queried_data: (pandas dataframe) queried data
    
    '''
    varstring = "?get=" + ",".join(varlist) + "&for=county:*"
    query_request = "https://api.census.gov/data/2015/acs5" + varstring

    r = requests.get(query_request)
    data_json = r.json()
    
    queried_data = pd.DataFrame(data_json[1:], columns = data_json[0])
    
    return queried_data
    
def query_unemp_data():
    '''
    This function queries variables on employment status. 
    
    Return:
        - unemp_data: (pandas dataframe) queried unemployment data
    '''
    
    civilian_loborforce_varlist = [
                "COUNTY", 
    				"ST", 
                'B23001_006E',  # Male Civilian in labor force 16 - 19 
                'B23001_013E',  # Male Civilian in labor force 20 - 21
                'B23001_020E',  # Male Civilian in labor force 22 - 24
                'B23001_027E',  # Male Civilian in labor force 25 - 29
                'B23001_034E',  # Male Civilian in labor force 30 - 34
                'B23001_041E',  # Male Civilian in labor force 35 - 44
                'B23001_048E',  # Male Civilian in labor force 45 - 54
                'B23001_055E',  # Male Civilian in labor force 55 - 59
                'B23001_062E',  # Male Civilian in labor force 60 - 61
                'B23001_069E',  # Male Civilian in labor force 62 - 64
                'B23001_074E',  # Male Civilian in labor force 65 - 69
                'B23001_079E',  # Male Civilian in labor force 70 - 74
                'B23001_084E',  # Male Civilian in labor force 75+
                'B23001_092E',  # Female Civilian in labor force 16 - 19 
                'B23001_099E',  # Female Civilian in labor force 20 - 21 
                'B23001_106E',  # Female Civilian in labor force 22 - 24 
                'B23001_113E',  # Female Civilian in labor force 25 - 29 
                'B23001_120E',  # Female Civilian in labor force 30 - 34 
                'B23001_127E',  # Female Civilian in labor force 35 - 44 
                'B23001_134E',  # Female Civilian in labor force 45 - 54 
                'B23001_141E',  # Female Civilian in labor force 55 - 59 
                'B23001_148E',  # Female Civilian in labor force 60 - 61
                'B23001_155E',  # Female Civilian in labor force 62 - 64 
                'B23001_160E',  # Female Civilian in labor force 65 - 69 
                'B23001_165E',  # Female Civilian in labor force 70 - 74 
                'B23001_170E'   # Female Civilian in labor force 75+ 
                ]
    
    unemp_varlist = [
                "COUNTY", 
    				"ST", 
                'B23001_008E',  # Male unemployment 16 - 19
                'B23001_015E',  # Male unemployment 20 - 21
                'B23001_022E',  # Male unemployment 22 - 24
                'B23001_029E',  # Male unemployment 25 - 29
                'B23001_036E',  # Male unemployment 30 - 34
                'B23001_043E',  # Male unemployment 35 - 44
                'B23001_050E',  # Male unemployment 45 - 54
                'B23001_057E',  # Male unemployment 55 - 59
                'B23001_064E',  # Male unemployment 60 - 61
                'B23001_071E',  # Male unemployment 62 - 64
                'B23001_076E',  # Male unemployment 65 - 69
                'B23001_081E',  # Male unemployment 70 - 74
                'B23001_086E',  # Male unemployment 75+
                'B23001_094E',  # Female unemployment 16 - 19 
                'B23001_101E',  # Female unemployment 20 - 21 
                'B23001_108E',  # Female unemployment 22 - 24 
                'B23001_115E',  # Female unemployment 25 - 29 
                'B23001_122E',  # Female unemployment 30 - 34 
                'B23001_129E',  # Female unemployment 35 - 44 
                'B23001_136E',  # Female unemployment 45 - 54 
                'B23001_143E',  # Female unemployment 55 - 59 
                'B23001_150E',  # Female unemployment 60 - 61
                'B23001_157E',  # Female unemployment 62 - 64 
                'B23001_162E',  # Female unemployment 65 - 69 
                'B23001_167E',  # Female unemployment 70 - 74 
                'B23001_172E'   # Female unemployment 75+ 
                ]
 
    civilian = request_data(civilian_loborforce_varlist)
    civilian = civilian.drop(['state', 'county'], axis = 1)
    
    nunemp = request_data(unemp_varlist)
    nunemp = nunemp.drop(['state', 'county'], axis = 1)
    
    unemp_data = civilian
    unemp_data = unemp_data.merge(nunemp, on = ['COUNTY', 'ST'], how = 'left')
    
    varlist = civilian_loborforce_varlist + unemp_varlist[3:]

    for var in varlist[3:]:
        unemp_data[var] = pd.to_numeric(unemp_data[var])
        
    unemp_data['unemp_rate'] = unemp_data.iloc[:, 29 : ].sum(axis = 1) / \
                               unemp_data.iloc[:, 2 : 28].sum(axis = 1)
    return_var_list = ['COUNTY', 'ST', 'unemp_rate']
    
    unemp_data = unemp_data[return_var_list]
    
    return unemp_data

def query_poverty_data():
    '''
    This function queries variables on poverty. 
    
    Return:
        - poverty_data: (pandas dataframe) queried poverty data
    '''
    
    varlist = [
                "COUNTY", 
    				"NAME", 
				   "ST", 
                'B17001_003E', # Male, Income in the past 12 months below poverty level
                'B17001_017E', # Female
                'B17001_032E', # Male, Income in the past 12 months at or above poverty level
                'B17001_046E'  # Female
                ]
    
    poverty_data = request_data(varlist)
    
    for var in varlist[3:]:
        poverty_data[var] = pd.to_numeric(poverty_data[var])
        
    poverty_data['Poverty_rate'] = (poverty_data['B17001_003E'] + poverty_data['B17001_017E']) / \
                                   poverty_data.iloc[:, 3 : 7].sum(axis = 1)
    return_var_list = ['COUNTY', 'ST', 'Poverty_rate']
    
    poverty_data = poverty_data[return_var_list]
    
    return poverty_data
    
    
def query_education_data():
    '''
    This function queries variables on county education information. 
    
    Return:
        - educ_data: (pandas dataframe) queried education data
    '''
    
    varlist = [
                "COUNTY", 
				   "NAME", 
				   "ST", 
                "B15002_003E",  # Male No schooling complete
                "B15002_004E",  # Male Nursery to 4th grade
                "B15002_005E",  # Male 5th and 6th grade
                "B15002_006E",  # Male 7th and 8th grade
                "B15002_007E",  # Male 9th grade
                "B15002_008E",  # Male 10th grade
                "B15002_009E",  # Male 11th grade
                "B15002_010E", # Male 12th grade, no diploma
                "B15002_011E", # Male High school graduate (includes equivalency)
                "B15002_012E", # Male Some college, less than 1 year
                "B15002_013E", # Male Some college, 1 or more years, no degree
                "B15002_014E", # Male Associate's degree
                "B15002_015E", # Male Bachelor's degree
                "B15002_016E", # Male Master's degree
                "B15002_017E", # Male Professional school degree
                "B15002_018E", # Male Doctorate degree
                "B15002_020E",  # Female No schooling complete
                "B15002_021E",  # Female Nursery to 4th grade
                "B15002_022E",  # Female 5th and 6th grade
                "B15002_023E",  # Female 7th and 8th grade
                "B15002_024E",  # Female 9th grade
                "B15002_025E",  # Female 10th grade
                "B15002_026E",  # Female 11th grade
                "B15002_027E", # Female 12th grade, no diploma
                "B15002_028E", # Female High school graduate (includes equivalency)
                "B15002_029E", # Female Some college, less than 1 year
                "B15002_030E", # Female Some college, 1 or more years, no degree
                "B15002_031E", # Female Associate's degree
                "B15002_032E", # Female Bachelor's degree
                "B15002_033E", # Female Master's degree
                "B15002_034E", # Female Professional school degree
                "B15002_035E", # Female Doctorate degree
            ]

    educ_data = request_data(varlist)
    
    for var in varlist[3:]:
        educ_data[var] = pd.to_numeric(educ_data[var])
    
    educ_data['High_school_orless'] = educ_data.iloc[:, 3 : 12].sum(axis = 1) + \
                                      educ_data.iloc[:, 19 : 28].sum(axis = 1)
    educ_data['College_ormore'] = educ_data.iloc[:, 15 : 19].sum(axis = 1) + \
                                  educ_data.iloc[:, 31 : 36].sum(axis = 1)
    return_var_list = ['COUNTY', 'ST', 'High_school_orless', 'College_ormore']
    
    educ_data = educ_data[return_var_list]
    
    return educ_data
    
def query_population_data():
    '''
    This function queries variables on population information. 
    
    Return:
        - pop_data: (pandas dataframe) queried population data
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
    
    pop_data = request_data(varlist)   
    
    for var in varlist[3:]:
        pop_data[var] = pd.to_numeric(pop_data[var])
        
    age_under18_vars = ['B01001_003E', 'B01001_004E', 'B01001_005E', 'B01001_006E', \
                        'B01001_027E', 'B01001_028E', 'B01001_029E', 'B01001_030E']
    
    age_over65_vars  = ['B01001_020E', 'B01001_021E', 'B01001_022E', 'B01001_023E', \
                        'B01001_024E', 'B01001_025E', 'B01001_044E', 'B01001_045E', \
                        'B01001_046E', 'B01001_047E', 'B01001_048E', 'B01001_049E']
    
    pop_data['Pop_under18'] = pop_data[age_under18_vars].sum(axis = 1)
    pop_data['Pop_over25']  = pop_data.iloc[:, 11:26].sum(axis = 1) + \
                              pop_data.iloc[:, 34:49].sum(axis = 1)
    pop_data['Pop_over65']  = pop_data[age_over65_vars].sum(axis = 1)
    pop_data['Population1'] = pop_data.sum(axis = 1)
    
    return_var_list = ['COUNTY', 'ST', 'Pop_under18', 'Pop_over25', 'Pop_over65']
    
    pop_data = pop_data[return_var_list]
    
    return pop_data
    
def query_data(filename):
    '''
    Send query to Census bureau API and save the data
    Census data Variable list: https://api.census.gov/data/2015/acs5/variables.html
    
    Variable queried directly in this function:
        - COUNTY: FIPS County code
        - NAME: Geographic Area Name
        - ST: State FIPS code
        - B00001_001E: Total population
        - B00002_001E: Total number of households
        - B08201_001E: Household size
        - B15002_001E: Age 25 or over (serve as the universe for tabulating educational attainment)
        - B17001_001E: Number of persons for whom poverty status is determined
        - B17001_002E: Number of persons in poverty
        - B19013_001E: Median household income (in 2015 USD)
        - B19301_001E: Per capita income (in 2015 USD)
        - B25058_001E: Median rent value
        - B25077_001E: Median home value 
        
    Variables indirectly queried:
        - Education data
        - Poverty data
        - Population data
        - Unemployment data
        
    Input:
        - filename: (string) the output filename
        
    Output:
        - Datafile titled filename
         
	 '''
    ## Generate query
    varlist = [
    				"COUNTY", 
				   "NAME", 
				   "ST", 
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

    r = requests.get(query_request)
    acs_data = r.json()
    varname_list = ['COUNTY', 'NAME', 'ST', \
                    'Num_household',  \
                    'Household_size', 'Age25_over', \
                    'Num_pov_det', 'Num_in_pov', \
                    'Median_hhinc', 'Incpc', \
                    'median_rent_value', 'median_home_value', \
                    'state', 'county']

    # Fron nested list to pandas dataframe
    data = pd.DataFrame(acs_data[1:], columns = varname_list)

    numeric_varlist = ['Num_household', \
                       'Household_size', 'Age25_over', \
                       'Num_pov_det', 'Num_in_pov', \
                       'median_rent_value', 'median_home_value', \
                       'Median_hhinc', 'Incpc']
    for var in numeric_varlist:
        data[var] = pd.to_numeric(data[var])

    pop_data = query_population_data()
    educ_data = query_education_data()
    unemp_data = query_unemp_data()
    
    data = data.merge(pop_data, on = ['COUNTY', 'ST'], how = 'left')
    data = data.merge(educ_data, on = ['COUNTY', 'ST'], how = 'left')
    data = data.merge(unemp_data, on = ['COUNTY', 'ST'], how = 'left')
    
    data = generate_newvars(data)
    
    data.to_csv(filename, sep=',', encoding = 'utf-8')

if __name__ == "__main__":
    filename = "acs_data/ACS_data.txt"
    query_data(filename)
