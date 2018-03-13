This is the instruction documentation for using the app "Happy Retirement" by TRG Group




                      -- Deverlopers' Foreword--
A lot of our effort and focus has been put into developing a robust, user-friendly and ready-to-use platform for users to locate and understand more about their potential ideal county to relocate to after their retirement. We really wish you could be able to run and play with the app. 
If you cannot run the app after the instruction below, plesae do reach out to us to assist you in successfully running the app. We could be contacted at:


#########################################
Chen Anhua:  anhua@uchicago.edu
Xu Zunda:    zunda@uchicago.edu
Zhang Xiang: snzhang@uchicago.edu
#########################################




-- Context --


        I. How to run our app and play with it
        II. Introduction to our code
                A. an overview of our code structure
                B. Breif introduction to each section
                C. People in charge of each section
                D. Information on references






# ==================================================================================
I. How to run our app and play with it (IMPORTANT)
# ==================================================================================


1.Python packages required to run the app
        i)   Django
        ii)  Matplotlib
        iii) Matplotlib.basemap
        iii) sklearn.neighbors (or most updated "sklearn")
        iv)  numpy
        v)   pandas
        vi)  geopy


(Also, please ensure you have internet connection, since we will call image from github)


2. How to run the app


        i)   Download our folder "project" into your local directory (e.g., "c:/user/download/")
        ii)  navigate your terminal to the directory "project/ui" (e.g., "c:/user/download/project/ui")
        iii) type in the following code in terminal:
                
                python3 manage.py runserver --nothreading


        (please note that you have to use nothreading becasue certain features of matplotlib will leads to its crash when operated on multiple threads)
        iv) "ctrl" + click on "http://127.0.0.1:8000/" in the terminal. Then you should be up and running!!


3. Features of our app and how to play with it


        i) after running the command above, you should enter our main page. There are two ways to find the perfect counties for you to retire to: Featured table list and search engine


        ii) Featured table lists:
         If you click on the size graph-tags in our main page or click on any of the other features on the left column in our main page. You will be brought to our featured table list, containing a heat-map of the distribution of the feature you have chose across all over US, also a "Best 100"and "Worst 100" lists. For example, if you click on "Neighbor Income", it will show your the household income distribution all over US and the 100 counties with the highest and lowest household incomes.


        Every counties in the list is a hyperlink you could click into, which will show you the details and visualization of the county of interest.


        If you click on the TRG Group on the left head section of the page, it will bring you back to the main page


        iii) Search engine
        In the right center part of the main page you could search the counties based on your preference. After clicking the "search" recommended counties will appear on the left side. If you choos "show all", it will presents all recommended counties orelse it will only show the randomly-chose 15 counties.


        One feature to highlight is that if you search doesn't return any matched counties, on the left side, it will show an instruction on how to relax your inputs, after which if the uesr follows, recommendatioins will guarantee to exist.


        iv) County detail page
        Whenever you click on county name either in recommended list or table lists, it will bring you to our country detail page. On the detail page, it will show all highlights of count's statistics, a map indicating the "general" and "exact" location of the county and weather and racial distribution visualization


        You could also search for similar counties based on the features you selected on the bottom of the page, from which you could also click into other county's detail page.








# ==================================================================================
II. An introduction to our code
# ==================================================================================


A. General structure
        Our project folder is divided into three main parts:
        1. data
        2. utility
        3. ui


        where /data folder included all the code and data we use to construct our database used in the ui. /viz folder includes our working horse visualization function to generate the all-US heat map and ~3000 counties' location map (with a zoom-in feature)
        Finally /ui folder includes all our main back-end and front-end of the app. 


B. Brief introduction to each section
        
        1. /data  (All data/scripts in this section are created from scratch)
                we firstly have several scripts to dealing with first-stage downloading/preliminary cleaning of the raw data, including:
                get_data_aqi.py; get_data_crime.py; 
                get_data_ACS.py; get_data_census.py; get_state_longlat.py;


                Then we have a main script called data_merge.py to merge all of the raw data together. We use county FIPS code/Name to merge ACS/Census/crime data, then we merge them with airport/weather/air quality data based on the neareset neighbor alogorithm based on Latitude and Longitude data.


                ## NOTICE ##
                Since we got our data from many different sources, we don't recommend run the raw data_downloading scripts because it may take days to finish......


                If you want to test the correctedness of our data generating code, you could run the data_merge.py by entering $python3 data_merge.py


        2. /utility  (created from scratch, with detail reference information in the code)
        
                Including key python file for our visualization and also the code automatically generate HTML page. 
                
                Running these code files will take more than one day due to the large sample size. So we provide several
                test code for you, and actually, the main function is just looping over the dataset to get all results.
                All the output of this file is stored in the “output” folder
                
                ## NOTICE ##
                Please do not run the "utility/draw_distribution_basemap.py" through since it will take more than one day. 
                If you want to test the function, here we provide several sample test code. 
                
                First, open the directory to "/utility":
                - To test "plot_county_choropleth" function, you could run: 
                        - import draw_distribution_basemap as drawmap
                        - drawmap.plot_county_choropleth("Median_hhinc")
                        - Note: At line 370, we offer you more variable options, they are in "varlist" 
                
                - To test "plot_county_choropleth" function, you could run: 
                        - drawmap.plot_county_choropleth_bystate("Median_hhinc", "IL", "17")
                        - Note: This will draw the distribution of median household income in Illinois 
                        
                - To test "plot_county_location" and "import_data" function, you could run:
                        - filename = "../data/database/database_cleaned.csv"
                        - data = drawmap.import_data(filename)
                        - drawmap.plot_county_location("17031", data)
                        - This will draw the location of Cook County, Illinois
                
        3. /ui  (we follow the django tutorial to set up the skeleton of code, the model/data/controller/urls scripts are mainly created from scratch)


                This folder is the main user-interface of our app


                i) /DB (created from scratch)
                        This includes all the datasets and our merged major database: database_cleaned.csv


                ii) /static (created from scratch)
                        folder to store some static features of our app


                iii) /search 
                This is our main app folder
                        a) models.py (created from scratch)
                                This script includes all the models we embedded in our app. For example, function to search for counties, function to find similar counties and functions to provide users with guidance on how to relax their inputs


                                It also includes all the classes designed for our app (e.g., county_profile, county_detail)


                        b) views.py (created from scratch, the construction of dropdown bars are modified from the script in pa3 )
                                This script is the "backbone" of our app, serving as a controller to load in data, pass data to model, render model-returned output to html


                        c) /templates (heavily modified)
                                a folder to contain our craftly-designed html webpage templates. For different counties, we are using the same county detail template but dynamically passing different data to it.


                        d) /urls.py (created from scratch)
                                This script designs the network structure of urls embedded under our app.




C. People in charge
        In general, Chen Anhua is in charge of the back-end structure design of the app. Zhang Xiang is in charge of the core visualization feature and associated html design and Xu Zunda is mainly in charge of our front-end design: HTML templates design/.css style files. And all three are in charge of data preparation. For details:
        Chen Anhua:
                1.Data: get_data_aqi.py, get_data_crime.py, data_merge.py
                2. ui: /ui/search/models.py, /ui/search/views.py, /ui/search/urls.py
        Xu Zunda:
                1. Data: data/get_data_climate.py
                2. ui: /ui/search/templates/; /ui/static/custom.css
        Zhang Xiang:
                1. Data: data/get_data_acs.py, data/get_data_census.py, data/get_state_longlat.py
                2. ui: /ui/search/templates/HTML_xxx.html; /utility/Generate_HTML.py
                3. utility： /utility/draw_distribution_basemap.py


D. Reference information


We include a basic description of reference information in “()” in the previous section C behind each section of our code. 


We also include some more detailed references in the scripts. 


We created the HTML templates with certain reference in terms of style to: https://www.quackit.com/html/templates/business_website_templates.cfm