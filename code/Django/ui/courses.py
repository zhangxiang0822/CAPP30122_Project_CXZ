### CS122, Winter 2018: Course search engine: search
###
### Chen Anhua (anhua)

from math import radians, cos, sin, asin, sqrt
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course_information.sqlite3')

## -------------------------------------------------------------
## Breif introduction 
## My basic idea is to divide the sql query string into four parts:
##  s1: the "SELECT"  string
##  s2: the "JOIN" string
##  s3: the "ON" string ---- joining conditions
##  s4: the "WHERE" string ---- filtering conditions
## I wrote three auxilary functrions:
##  1. prefix_checks:  a function to decide whether I need to add "and" in front of a string
##  2. update_query: a function to update the four query strings mentioned above for
##     any case.
##  3. update_params: a function to update the parameters for any case
## Based on the abstraction from three auxilary functions, 
## I designed a "updating_dict" in the main function to utilize the auxilary functions 
## many times for different cases.
## -------------------------------------------------------------


def prefix_check(s, s_init):
  '''
  a function to check whether the string (s) is in its initial value (s_init) 
  to decide whether we need to add "and" in front of the new string

  inputs:
      s: (string) old string upon which to join new string segments
      s_init: (string) initial value of the string (e.g., "where" / "on") 
      representing the start of a SQL query
  Returns:
      either "" or "and"
  '''
  if s == s_init:
    return ""
  else:
    return "and"

def update_query(input_attr, updating_dict, args_from_ui, old_strings):
    '''
    THis function will update the query strings and params according to updating_dict
    And return the updated query strings and params
    inputs:
        input_attr: (string) the name of the input attribute
        updating_dict: (dictionary) a dictionary with key being the name of input attribute
        and values being additional query strings to be added to old_strings
        Each key's value includes a tuple of the following four lists
          s1_delta: (list of strings) or None
          s2_delta: (list of strings) or None
          s3_delta: (list of strings) or None
          s4_delta: (list of strings) or None
          
        args_from_ui: (dictionary) the input dictionary from users
        old_strings: (tuple of strings) represents four different parts of the query TO BE UPDATED:
          s1: the "SELECT"  string
          s2: the "JOIN" string
          s3: the "ON" string ---- joining conditions
          s4: the "WHERE" string ---- filtering conditions
    Returns:
        new_strings: (a tuple of strings) represents four updated query strings, in the
        same structure as old_strings
    '''
    

    s1, s2, s3, s4 = old_strings
    s1_delta, s2_delta, s3_delta, s4_delta = updating_dict[input_attr]    # additional strings to add on

    if s1_delta is not None:
      s1_new = ", ".join([s1] + s1_delta)
    else:
      s1_new = s1

    if s2_delta is not None:
      s2_new = " ".join([s2] + s2_delta)
    else:
      s2_new = s2

    if s3_delta is not None:
      s3_new = " ".join([s3] + [prefix_check(s3, "on")] + s3_delta)
    else:
      s3_new = s3

    if s4_delta is not None:

      if input_attr == "day":    # case where input is "day"
        vals = args_from_ui[input_attr]
        N = len(vals)
        place_holder = ", ".join(["?"] * N)    # a place to hold "?,?,..."
        s4_new = " ".join([s4] + [prefix_check(s4, "where")] + 
          s4_delta[:-1] + [place_holder] + s4_delta[-1:])

      elif input_attr == "terms":   # special case when input is "terms"
        vals = args_from_ui[input_attr].split()
        N = len(vals)
        place_holder = ", ".join(["?"] * N)    # a place to hold "?,?,..."
        s4_new = " ".join([s4] + [prefix_check(s4, "where")] + 
          s4_delta[:-1] + [place_holder] + s4_delta[-1:])
          
      else:
        s4_new = " ".join([s4] + [prefix_check(s4, "where")] + s4_delta)
    else:
      s4_new = s4
 
    new_strings =  (s1_new, s2_new, s3_new, s4_new)
    return new_strings



def update_params(input_attr, params, args_from_ui):
    '''
    This function will update the params that will be fed to sqlite3,
     according to the user input

    Inputs:
        input_attr: (string) the name of the input attribute
        old_params: (list) the list of the 
        args_from_ui: (dictionary) the input dictionary from users

    Updates:
        params (list) updated list
    '''
    vals = args_from_ui[input_attr]    # the value of the user input
    if input_attr == "day":
      params += vals
    elif input_attr == "terms":    # special case of terms input
      vals = vals.split()
      N = len(vals)
      params += vals
      params += [N]
    else:
      params += [vals]

    

def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is array with variable number of elements
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enroll is an integer
      - walking_time is an integer
      - building ia string
      - terms is a string: "quantum plato"]

    Returns a pair: list of attribute names in order and a list
    containing query results.


    '''
    keys = set(args_from_ui.keys())    # a set of user inputs
    
    if len(keys) == 0:    # the case where no input is given
      return ([], [])

    ## ------------------------------------------------------
    ## Setting  up connection and input function into sqlite3
    ## ------------------------------------------------------
    connection = sqlite3.connect(DATABASE_FILENAME)
    cur = connection.cursor()
    connection.create_function("time_between", 4, compute_time_between)
    
    ## ------------------------------------------------------
    ## initial query strings and parameters
    ## ------------------------------------------------------
    
    params = []    # list of parameters
    s1 = "select distinct dept, course_num"    # the "SELECT" string
    s2 = "from courses"    # the "FROM" field query string
    s3 = "on"    # joining conditions
    s4 = "where"    # filtering condtions

    ## -------------------------------------------------------------------
    ## Creating subgroups
    ##
    ## In order to enhance the efficiency of updating, I will pack the 
    ## inputs into some subgroups so that they will share the SAME updating
    ## procedure for certain operations. Grouping is based on table in writeup
    ## --------------------------------------------------------------------
    gp1 = set(["day", "time_start", "time_end", "walking_time", "building", 
      "enroll_lower", "enroll_upper"])
    gp2 = set(["walking_time", "building"])
    gp3 = set(["enroll_lower", "enroll_upper"])
    gp4 = set(["terms", "dept"])
    

    ## --------------------------------------------------------------------
    ## Creating the updating dictionary
    ##
    ## The key of the dictionary represents the input attribute
    ## The value of each key represents the additional strings that need to 
    ## be added to the query strings (s1, s2, s3, s4) if certain input is given
    ## --------------------------------------------------------------------
    updating_dict = {
    "terms":(None, 
             ["join catalog_index as cat"], 
             ["courses.course_id = cat.course_id"], 
             ["cat.course_id in (\
          select cat2.course_id from catalog_index as cat2 where cat2.word in (",
          ") group by cat2.course_id having count(*) = ?)"]),
    "dept":(None,
            None,
            None,
            ["courses.dept = ?" ]),
    "day":( None,
            None,
            None,
            ["mp.day in (", ")" ]),
    "time_start":( None,
                   None,
                   None,
                   ["mp.time_start >= ?" ]),
    "time_end":( None,
                   None,
                   None,
                   ["mp.time_end <= ?" ]),
    "walking_time":(),
    "building":(),
    "enroll_lower":(None,
                    None,
                    None,
                    ["sections.enrollment >= ?"]),
    "enroll_upper":(None,
                    None,
                    None,
                    ["sections.enrollment <= ?"]),
    "gp1":( ["section_num", "day", "time_start", "time_end"],
            ["join sections join meeting_patterns as mp"],
            ["courses.course_id = sections.course_id and \
        sections.meeting_pattern_id = mp.meeting_pattern_id"],
            None),
    "gp2":(["a.building_code as building", 
        "time_between(a.lon, a.lat, b.lon, b.lat) as walking_time"],
           ["join gps as a join gps as b"],
           [" sections.building_code = a.building_code"],
           ["b.building_code = ? and walking_time <= ?"]),
    "gp3":( ["enrollment"],
            None,
            None,
            None),
    "gp4":(["title"],
           None,
           None,
           None)
    }
    ## ------------------------------------------------------
    ## Using auxilary functions to update quesry string
    ## ------------------------------------------------------

    if len(gp1.intersection(keys)) > 0:   # some attribute in group is in inputs

      s1, s2, s3, s4 = \
        update_query("gp1", updating_dict, args_from_ui, (s1, s2, s3, s4))  # updating query

      for k in ["day", "time_start", "time_end"]:
        
        if k in keys:
          s1, s2, s3, s4 = \
            update_query(k, updating_dict, args_from_ui, (s1, s2, s3, s4))
          update_params(k, params, args_from_ui)


    if len(gp2.intersection(keys)) > 0:    # walking_time/building are in inputs
      s1, s2, s3, s4 = \
        update_query("gp2", updating_dict, args_from_ui, (s1, s2, s3, s4))
      
      update_params("building", params, args_from_ui)
      update_params("walking_time", params, args_from_ui)
      

    if len(gp3.intersection(keys)) > 0:    # group 3 is in inputs
      s1, s2, s3, s4 = \
        update_query("gp3", updating_dict, args_from_ui, (s1, s2, s3, s4))
      
      for k in ["enroll_lower", "enroll_upper"]:
        if k in keys:
          s1, s2, s3, s4 = \
            update_query(k, updating_dict, args_from_ui, (s1, s2, s3, s4))
          update_params(k, params, args_from_ui)

      
    if len(gp4.intersection(keys)) > 0:    # group 4 is in inputs
      s1, s2, s3, s4 = \
        update_query("gp4", updating_dict, args_from_ui, (s1, s2, s3, s4))
      
      for k in ["dept", "terms"]:
        if k in keys:
          s1, s2, s3, s4 = \
            update_query(k, updating_dict, args_from_ui, (s1, s2, s3, s4))
          update_params(k, params, args_from_ui)
            
    ## ------------------------------------------------------
    ## Execute the query to get output table
    ## ------------------------------------------------------
    if s3 == "on":    # case without any joining 
      s3 = ""

    if s4 == "where":    # case without any filtering
      s4 = ""

    s = " ".join([s1, s2, s3, s4])       
    r = cur.execute(s, params)
    output_tab = r.fetchall()
    
    if len(output_tab) == 0:
      return ([], [])

    return (get_header(cur), output_tab)


    
########### auxiliary functions #################
########### do not change this code #############

def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return mins


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i, _ in enumerate(s):
        if s[i] == ".":
            s = s[i + 1:]
            break

    return s


########### some sample inputs #################

EXAMPLE_0 = {"time_start": 930,
             "time_end": 1500,
             "day": ["MWF"]}

EXAMPLE_1 = {"dept": "CMSC",
             "day": ["MWF", "TR"],
             "time_start": 1030,
             "time_end": 1500,
             "enroll_lower": 20,
             "terms": "computer science"}
