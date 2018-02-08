from census import Census
from us import states
import requests
import json
import pandas as pd
import numpy as np

"""
COUNTY: FIPS County code
NAME: Geographic Area Name
ST: State FIPS code
B00001_001E: Total population
B00002_001E: Total number of households
B01001_001E: Sex by age (total)
B01001_001E: In labor force
			"NAME", 
			"ST", 
			"B00001_001E",
			"B01001_001E",
			"B00002_001E",
			"B08201_001E"
B08201_001E: Household size
"""

## Generate query
varlist = [
			"COUNTY", 
			]

varstring = "?get=" + ",".join(varlist) + "&for=county:*"

query_request = "https://api.census.gov/data/2015/acs5" + varstring
print(query_request)

r = requests.get(query_request)
acs_data = r.json()

print(acs_data[0])

# Fron nexted list to pandas dataframe
data = pd.DataFrame(acs_data[1:], columns = acs_data[0])

numeric_varlist = ['B00001_001E', 'B01001_001E', 'B00002_001E', 'B08201_001E']
for var in numeric_varlist:
    data[var] = pd.to_numeric(data[var])

data.to_csv("ACS_data.txt", sep='\t', encoding='utf-8')

# Plot County Level Choropleth
data = pd.read_csv("ACS_data.txt")

import plotly.plotly as py
import plotly.graph_objs as go

print(data)


