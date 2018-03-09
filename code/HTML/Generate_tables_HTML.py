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

    varlist = ["NAME", varname, "COUNTY", "ST"]
    data = data[varlist].head(100)

    html_table = "<div>" 
    html_table +=   """
                    <table align = center class = "table" width = "70%" border = "1" frame = "void" 
        			   rules = "rows">
            		<thead>
            			<th style="text-align: left;"><font size = "-1">Rank</font></th>
            			<th style="text-align: left;"><font size = "-1">County</font></th>
            			<th style="text-align: left;"><font size = "-1">State</font></th>
            			<th style="text-align: right;"><font size = "-1">""" + vartitle + """</font></th>
            		</thead> \n
                     """
                
    rank = 0                
    for index, item in data.iterrows():
        rank += 1

        names = item["NAME"].split(",")
        countyname, statename = names[0], names[1]

        countyfips = str(item["COUNTY"])
        statefips = str(item["ST"])
        value = float("{0:.2f}".format(item[varname]))
        
        html_table += "\t<tr> \n" + \
        		'\t\t<td align="left">' + str(rank) + '</td> \n' + \
        		'\t\t<td align="left">' + '<a href = "/' + statefips + '/' + \
                countyfips + '">' + countyname + '</a></td> \n' + \
        		'\t\t<td align="left">' + statename + '</td> \n' + \
        		'\t\t<td align="right">' + str(value) + '</td> \n' + \
                '\t</tr> \n'
        
    html_table += "\t</table>\n\t</div>"

    filename = "../../data/HTML_table/HTML_table_" + varname + str(ascend) + ".txt"
    file = open(filename, "w")

    file.write(html_table)
    file.close()             

def gen_html_page(varname, graph_title, title1, title2, highfirst):

    html = ""
    html += """
    {% load staticfiles %}
    {% load search_tags %}
    {% static "" as baseUrl %}
    
    <!DOCTYPE html>
    <html lang="en-US">
    <head>
    	<meta charset="utf-8">
    	<meta http-equiv="X-UA-Compatible" content="IE=edge">
    	<meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Krona+One" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css?family=Bowlby+One+SC|Lobster|Merriweather|Pacifico" rel="stylesheet">
    	<title>CAPP30122 HTML</title>
    
    	<!-- Bootstrap Core CSS -->
        <!--<link href="css/bootstrap.min.css" rel="stylesheet">
    
        <!-- Custom CSS: You can use this stylesheet to override any Bootstrap styles and/or apply your own styles -->
        <!--<link href="css/custom.css" rel="stylesheet"> -->
        <link rel="stylesheet" type="text/css" href="{% static "/custom.css" %}" />
    	<script>var __adobewebfontsappname__="dreamweaver"</script>
    	<script src="http://use.edgefonts.net/source-sans-pro:n2:default.js" type="text/javascript"></script>
    	<!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    	<!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    	<!--[if lt IE 9]>
        	<script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
        	<script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
        <![endif]-->
    </head>
    	
    <body>
    <!-- Main Container -->
    	
    	<!-- Top Navigator -->
    	<!-- We learn this from w3c school -->
    	<div class="topnav">
      		<a href = "/">TRG Group</a>
    	</div>
    	
    	<!-- Feature -->
    	<div style = "background-image: url('{{ baseUrl }}/retirement.jpg')" class = "jumbotron feature">
    		<div class = "container">
    			<h1>HAPPY RETIREMENT</h1>
    			<p>Find the best place for your retired life</p>
    		</div>
    	</div>
        
            <!-- Figure -->
            <section>
            <div class = "container">
                <div class="row">
                    <div class="col-xs-12">
                        <h1 align="center"><font color = "black">
                        The Geography of""" +  graph_title + """ in America
                    </font></h1>
                </div>
            </div>
        
            <center>
            <img src = "{{ baseUrl }}/national_choropleth""" + varname + """.png"           
                 style="width: 80%; margin-bottom: 0%; margin-top: 0%;">    
            </center>
        </div>
        </section>
        
        <div class="container">
            <div class="row">
                <div class="col-xs-12"><font color = "black" size = '-1'>
                    <h1 align="center"><font color = "black">List of Counties with the """ + title1 + """</font></h1>
                </font>
                </div>
            </div>
        </div>
        
        <!-- List of table here-->
        """

    if highfirst:
        table1_name = "../../data/HTML_table/HTML_table_" + varname + "False.txt"
    else:
        table1_name = "../../data/HTML_table/HTML_table_" + varname + "True.txt"
    file = open(table1_name, "r")
    table1 = file.read()
    file.close() 

    if highfirst:
        table2_name = "../../data/HTML_table/HTML_table_" + varname + "True.txt"
    else:
        table2_name = "../../data/HTML_table/HTML_table_" + varname + "False.txt"

    file = open(table2_name, "r")
    table2 = file.read()
    file.close() 

    html += table1

    html += """
        <div class="container">
        <div class="row">
            <div class="col-xs-12">
                <h1 align="center">List of Counties with the """ +  title2 + """</h1>
            </div>
        </div>
    </div>
    """

    html += table2

    html += """
            <style>
        .table { 
            border-bottom: 1px; 
            text-color: black; 
            text-align: center; 
            font-family: Montserrat,sans-serif; 
            border-top: 1px solid black;
            font-size: 12px;
        }
        .table th { border: 0px }
        .table td {
            border: none;
        }
        .table tr{
            border-bottom: 1px solid black;
            border-top: 1px solid black;
            border-collapse: collapse;
        }
        .fixed-table-container { border:0px ; }
        .table_header { font-size: 13px; text-align: center; }
        </style>

    </body>
    </html>
    """

    filename = "../../data/HTML_page/HTML_" + varname + ".txt"
    file = open(filename, "w")

    file.write(html)
    file.close()  

if __name__ == "__main__":
    var_title_pair = [\
                      ("Median_hhinc", "Median Household Income"), \
                      ("median_rent_value", "Median Monthly Rent Rent"), \
                      ("median_home_value", "Median Housing Value"), \
                      ("Pov_rate", "Poverty Rate (%)"), \
                      ("Share_college_ormore", "Share with College Degree (%)"), \
                      ("Share_over65", "Share Aged 65+"), \
                      ("Share_under18", "Share Aged 18 or Less"), \
                      ("crime_rate", "Crime Rate (%)"), \
                      ("winter_avg_temp", "Winter Average Temperature (F)"), \
                      ("summer_avg_temp", "Summer Average Temperature (F)"), \
                      ("annual_avg_temp", "Anuual Average Temperature (F)"), \
                      ("aqi_good", "Share of Days with Good Air Quality (%)")
                      ]

    for item in var_title_pair:
        print(item)
        for ascend in [True, False]:
            draw_table(item[0], item[1], ascend)

    # Neighborhood charasteristics
    gen_html_page("Median_hhinc", "Median Household Income", "Highest Median Houshold Income", \
                  "Lowest Median Household Income", True)
    gen_html_page("median_rent_value", "Median Monthly Rent", "Highest Median Monthly Rent", \
                  "Lowest Median Monthly Rent", True)
    gen_html_page("median_home_value", "Median Housing Value", "Highest Median Housing Value", \
                  "Lowest Median Housing Value", True)
    gen_html_page("Pov_rate", "Poverty Rate", "Lowest Poverty Rate", \
                  "Highest Poverty Rate", False)
    gen_html_page("Share_college_ormore", "Share with College Degree", "Highest Share with College Degree", \
                  "Lowest Share with College Degree", True)
    gen_html_page("Share_college_ormore", "Share with College Degree", "Highest Share with College Degree", \
                  "Lowest Share with College Degree", True)
    gen_html_page("Share_over65", "Share of 65+ People", "Highest Share of 65+ People", \
                  "Lowest Share of 65+ People", True)
    gen_html_page("Share_under18", "Share of 18- People", "Highest Share of 18- People", \
                  "Lowest Share of 18- People", True)
    gen_html_page("crime_rate", "Crime Rate", "Lowest Crime Rate", \
                  "Highest Crime Rate", False)

    # Environment Charasteristics
    gen_html_page("winter_avg_temp", "Winter Temperature", "Highest Winter Temperature", \
                  "Lowest Winter Temperature", True)
    gen_html_page("summer_avg_temp", "Summer Temperature", "Lowest Summer Temperature", \
                  "Highest Winter Temperature", False)
    gen_html_page("annual_avg_temp", "Annual Temperature", "Highest Anuual Temperature", \
                  "Lowest Annual Temperature", True)
    gen_html_page("aqi_good", "Air Quality", "Best Air Quality", \
                  "Worst Air Quality", True)   