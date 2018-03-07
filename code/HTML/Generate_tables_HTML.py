import pandas as pd
import numpy as np

def draw_table(varname, vartitle, ascend):
    '''
    Function to generate HTML table for tables used in webpage "List_of_top_counties"

    Inputs:
    - varname: (string) name of the variable
    - vartitle: (string) Title of the table to be generated
    - ascend: (bool) True or False to select top or bottom county

    Returns:
    - No return

    Output:
    - Output file titled "../../data/HTML_table/HTML_table_" + str(acsend) + varname + ".txt"
    '''
    data = pd.read_csv("../../data/database_cleaned.csv")

    data = data.sort_values(by = [varname], ascending = ascend)

    varlist = ["NAME", varname]
    data = data[varlist].head(100)

    html_table = "<div>" 
    html_table +=   """
                    <table align = center class = "table" width = "70%" border = "1" frame = "void" 
        			   rules = "rows">
            		<thead>
            			<th style="text-align: left;">Rank</th>
            			<th style="text-align: left;">County</th>
            			<th style="text-align: left;">State</th>
            			<th style="text-align: right;">""" + vartitle + """</th>
            		</thead> \n
                     """
                
    rank = 0                
    for item in data.itertuples():
        rank += 1
        county, state = item[1].split(",")
        value = float("{0:.2f}".format(item[2]))
        html_table += "\t<tr> \n" + \
        		'\t\t<td align="left">' + str(rank) + '</td> \n' + \
        		'\t\t<td align="left">' + county + '</td> \n' + \
        		'\t\t<td align="left">' + state + '</td> \n' + \
        		'\t\t<td align="right">'+ str(value) + '</td> \n' + \
                '\t</tr> \n'

    html_table += "\t</table>\n\t</div>"

    filename = "../../data/HTML_table/HTML_table_" + varname + str(ascend) + ".txt"
    file = open(filename, "w")

    file.write(html_table)
    file.close()             

if __name__ == "__main__":
    var_title_pair = [\
                      ("Median_hhinc", "Median Household Income"), \
                      ("median_rent_value", "Median Rent per Month"), \
                      ("Pov_rate", "Poverty Rate (%)"), \
                      ("Share_college_ormore", "Share with College Degree (%)")
                      ]

    for item in var_title_pair:
        for ascend in [True, False]:
            draw_table(item[0], item[1], ascend)