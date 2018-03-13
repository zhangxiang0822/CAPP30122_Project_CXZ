import pandas as pd
import numpy as np

yrs_lst = [ 2011, 2012, 2013, 2014]
df_crime = pd.read_csv("./crime_data/crime_2010/crime_2010.tsv", sep='\t')
df_crime = df_crime.loc[:,["FIPS_ST", "FIPS_CTY", "CPOPCRIM", "VIOL", "PROPERTY"]]
df_crime["crime_rate_" + str(2010)] = (df_crime.VIOL + df_crime.PROPERTY) / df_crime.CPOPCRIM
df_crime = df_crime.drop(["CPOPCRIM", "VIOL", "PROPERTY"], axis = 1)


for yr in yrs_lst:
    df_new = pd.read_csv("./crime_data/crime_" + str(yr) + "/crime_" + str(yr) + ".tsv", sep='\t')
    df_new = df_new.loc[:,["FIPS_ST", "FIPS_CTY", "CPOPCRIM", "VIOL", "PROPERTY"]]
    df_new["crime_rate_" + str(yr)] = (df_new.VIOL + df_new.PROPERTY) / df_new.CPOPCRIM
    df_new = df_new.drop(["CPOPCRIM", "VIOL", "PROPERTY"], axis = 1)
    df_crime = pd.merge(df_crime, df_new, on = ["FIPS_ST", "FIPS_CTY"])

df_crime = df_crime[~df_crime.isin([np.nan, np.inf, -np.inf]).any(1)]
## Save cleaned crime rate data
df_crime.to_csv("./crime_data/crime_data_clnd.csv")