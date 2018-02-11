import pandas as pd
yrs_lst = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
## read in data
df_aqi = pd.read_csv("./aqi_data/annual_aqi_by_county_2009.csv")
for i in yrs_lst:
    df_new = pd.read_csv("./aqi_data/annual_aqi_by_county_" + str(i) + ".csv")
    df_aqi = pd.concat([df_aqi, df_new])

## Calculating the ratio of good/modereate/unhealty_SG/unhealthy/very_unhealthy/hazardous
var_lst = [
 'Good Days',
 'Moderate Days',
 'Unhealthy for Sensitive Groups Days',
 'Unhealthy Days',
 'Very Unhealthy Days',
 'Hazardous Days'
]
for var in var_lst:
    df_aqi[var +" ratio"] = df_aqi[var] / df_aqi['Days with AQI']

