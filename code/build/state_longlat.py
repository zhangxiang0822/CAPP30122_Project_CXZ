import bs4
import urllib3
import csv

# State abbreviation list is copy from the following website
# http://ageekandhisblog.com/text-copy-friendly-list-of-us-states-and-abbreviation/

STATE_ABBR_LIST = ["AL","AR","AZ","CA","CO","CT","DE","FL",\
                   "HI","IA","ID", "IL","IN","KY",\
                   "MA","MD","ME", "MI","MN","MO","MT", "MS", "NC","ND",\
                   "NE","NM","NV", "OH","OK","PA",\
                   "RI","SC","TN","TX","UT","VA","VT","WA",\
                   "WI","WV","WY"]

def get_longlatrange(state, state_latlong_range):
    pm = urllib3.PoolManager()

    myurl = "http://www.netstate.com/states/geography/" + state + "_geography.htm"
    html = pm.urlopen(url = myurl, method = "GET").data

    soup = bs4.BeautifulSoup(html, "html5lib")
    
    tag_list = soup.find_all("td", attrs = {"class": "alphainfo"})
    
    if tag_list:
        long_lat_string = tag_list[0].text.strip()
        long_lat_string = long_lat_string.replace("°", ' ')
        long_lat_string = long_lat_string.replace("'", ' ')
        long_lat_string = long_lat_string.replace("to", "Tooooo")
        long_lat_list = long_lat_string.strip()
        
        long_lat_list = long_lat_string.splitlines()
        lat_list = long_lat_list[0].split()
        long_list = long_lat_list[1].split()
    else:
        tag_list = soup.find_all(text = 'Longitude / Latitude')
        tag = tag_list[0].parent.next_sibling.next_sibling
        long_lat_string = tag.text.strip()
        
        long_lat_string = long_lat_string.replace("°", ' ')
        long_lat_string = long_lat_string.replace("'", ' ')
        long_lat_string = long_lat_string.replace("to", "Tooooo")
        long_lat_string = long_lat_string.replace('"', " ")
        long_lat_list = long_lat_string.split()
        
        cutoff = long_lat_list.index("WLatitude:")
        lat_list = long_lat_list[cutoff:]
        long_list = long_lat_list[0: cutoff]
        long_list.append("W")         
     
    lat_position  = [i for i, x in enumerate(lat_list) if x == "N"]
    lat_range = []
    long_range = []
    
    for pos in lat_position:
        if len(lat_list[pos - 2]) == 2:
            if len(lat_list[pos - 1]) == 2:
                latitude = int(lat_list[pos - 2][0:2]) \
                           + int(lat_list[pos - 1][0:2])/ 100
            else:
                latitude = int(lat_list[pos - 2][0:2]) \
                            + int(lat_list[pos - 1][0:1])/ 10
        elif len(lat_list[pos - 2]) == 3:
            if len(lat_list[pos - 1]) == 2:
                latitude = int(lat_list[pos - 2][0:3]) \
                            + int(lat_list[pos - 1][0:2])/ 100
            else:
                latitude = int(lat_list[pos - 2][0:3]) \
                            + int(lat_list[pos - 1][0:1])/ 10
        else:
            if len(lat_list[pos - 1]) == 2:
                latitude = int(lat_list[pos - 1][0:2])
            if len(lat_list[pos - 1]) == 3:
                latitude = int(lat_list[pos - 1][0:3])
                
        lat_range.append(latitude)
      
    long_position  = [i for i, x in enumerate(long_list ) if x == "W"]
    
    for pos in long_position:
        if len(long_list[pos - 2]) == 2:
            if len(long_list[pos - 1]) == 2:
                longitude = - int(long_list[pos - 2][0:2]) \
                            - int(long_list[pos - 1][0:2])/ 100
            else:
                longitude = - int(long_list[pos - 2][0:2]) \
                            - int(long_list[pos - 1][0:1])/ 10
        elif len(long_list[pos - 2]) == 3:
            if len(long_list[pos - 1]) == 2:
                longitude = - int(long_list[pos - 2][0:3]) \
                            - int(long_list[pos - 1][0:2])/ 100
            else:
                longitude = - int(long_list[pos - 2][0:3]) \
                            - int(long_list[pos - 1][0:1])/ 10
        else:
            if len(long_list[pos - 1]) == 2:
                longitude = - int(long_list[pos - 1][0:2])
            if len(long_list[pos - 1]) == 3:
                longitude = - int(long_list[pos - 1][0:3])
            
        long_range.append(longitude)
    
    # print(state, long_range, lat_range)
    long_range = (long_range[0], long_range[1])
    lat_range  = (lat_range[0], lat_range[1])
    
    state_latlong_range[state] = [lat_range, long_range]
    
state_latlong_range = {}

for state in STATE_ABBR_LIST:
    state = state.lower()
    get_longlatrange(state, state_latlong_range)

# Hardcode severla states
state_latlong_range["ak"] = [(54.40, 71.50), (-130, -173)]
state_latlong_range["dc"] = [(38.89, 38.89), (-77.03, -77.03)]
state_latlong_range["ga"] = [(30, 35),       (-81, -85)] 
state_latlong_range["ks"] = [(37, 40),       (-94.38, -102.1)]   
state_latlong_range["la"] = [(29, 33),       (-89, -94)]
state_latlong_range["mt"] = [(44.26, 49),    (-104.2, -116.2)]   
state_latlong_range["nh"] = [(42.3, 45.18),  (-70.37, -72)]
state_latlong_range["nj"] = [(38.55, 41.21), (-73.53, -75.35)]
state_latlong_range["ny"] = [(40.29, 46),    (-71.47, -79.45)]
state_latlong_range["or"] = [(42, 46.15),    (-116.45, -124.30)]
state_latlong_range["sd"] = [(42.29, 45.56),    (-97.28, -104.30)]

with open('../../data/state_longlat.csv', 'w', newline = '') as f:
    writer = csv.writer(f, delimiter = ',')
    fieldnames = ['state', 'lat_range_low', 'lat_range_high', \
                  'long_range_low', 'long_range_high']
    writer.writerow(fieldnames)
    for key, value in state_latlong_range.items():
        data= [key, value[0][0], value[0][1], value[1][0], value[1][1]]
        writer.writerow(data)
    