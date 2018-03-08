import json
import traceback
import sys
import csv
import os
import pandas as pd

from functools import reduce
from operator import and_


from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django import forms

#from courses import find_courses
from .models import find_counties, county_detail

NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')
#TEMP_DIR = os.path.join(os.path.dirname(__file__), '..', 's')
COLUMN_NAMES = dict(
    dept='Deptartment',
    course_num='Course',
    section_num='Section',
    day='Day',
    time_start='Time (start)',
    time_end='Time (end)',
    enroll='Enrollment',
)
DB_FILENAME = "database_cleaned.csv"
DF = pd.read_csv(os.path.join(RES_DIR, DB_FILENAME), encoding = 'ISO-8859-1')

def _valid_result(res):
    """Validate results returned by find_courses."""
    (HEADER, RESULTS) = [0, 1]
    ok = (isinstance(res, (tuple, list)) and
          len(res) == 2 and
          isinstance(res[HEADER], (tuple, list)) and
          isinstance(res[RESULTS], (tuple, list)))
    if not ok:
        return False

    n = len(res[HEADER])

    def _valid_row(row):
        return isinstance(row, (tuple, list)) and len(row) == n
    return reduce(and_, (_valid_row(x) for x in res[RESULTS]), True)


def _valid_military_time(time):
    return (0 <= time < 2400) and (time % 100 < 60)


def _load_column(filename, col=0):
    """Load single column from csv file."""
    with open(filename) as f:
        col = list(zip(*csv.reader(f)))[0]
        return list(col)


def _load_res_column(filename, col=0):
    """Load column from resource directory."""
    return _load_column(os.path.join(RES_DIR, filename), col=col)


def _build_dropdown(options):
    """Convert a list to (value, caption) tuples."""
    return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]

STEP = 0.1

BUILDINGS = _build_dropdown([None] + _load_res_column('building_list.csv'))
DAYS = _build_dropdown(_load_res_column('day_list.csv'))
DEPTS = _build_dropdown([None] + _load_res_column('dept_list.csv'))
REGION = _build_dropdown(_load_res_column('region_list.csv'))
STATES = _build_dropdown(_load_res_column('states_list.csv'))
UNEMP_RATE = _build_dropdown(_load_res_column('unemp_rate_list.csv'))
POV_RATE = _build_dropdown(_load_res_column('pov_rate_list.csv'))
SHARE_COLLEGE = _build_dropdown(_load_res_column('share_college_list.csv'))
AQI = _build_dropdown(_load_res_column('aqi_list.csv'))
SHARE_OVER65 = _build_dropdown(_load_res_column('share_over65_list.csv'))
RACE = _build_dropdown(_load_res_column('race_list.csv'))
VAR_OF_INTEREST = _build_dropdown(_load_res_column('var_list.csv'))

class IntegerRange(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.IntegerField())
        super(IntegerRange, self).__init__(fields=fields,
                                           *args, **kwargs)

    def compress(self, data_list):
        if data_list and (data_list[0] is None or data_list[1] is None):
            raise forms.ValidationError('Must specify both lower and upper '
                                        'bound, or leave both blank.')

        return data_list

class FloatRange(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.FloatField(),
                  forms.FloatField())
        super(FloatRange, self).__init__(fields=fields,
                                           *args, **kwargs)

    def compress(self, data_list):
        if data_list and (data_list[0] is None or data_list[1] is None):
            raise forms.ValidationError('Must specify both lower and upper '
                                        'bound, or leave both blank.')

        return data_list

class PopulationRange(IntegerRange):
    def compress(self, data_list):
        super(PopulationRange, self).compress(data_list)
        for v in data_list:
            if v < 0:
                raise forms.ValidationError(
                    'Population must be positive')
        if data_list and (data_list[1] < data_list[0]):
            raise forms.ValidationError(
                'Lower bound must not exceed upper bound.')
        return data_list


class MonetaryRange(FloatRange):
    def compress(self, data_list):
        super(MonetaryRange, self).compress(data_list)
        for v in data_list:
            if v < 0:
                raise forms.ValidationError(
                    'Monetary term must be positive')
        if data_list and (data_list[1] < data_list[0]):
            raise forms.ValidationError(
                'Lower bound must not exceed upper bound.')
        return data_list


class RateRange(FloatRange):
    def compress(self, data_list):
        super(RateRange, self).compress(data_list)
        for v in data_list:
            if not 0 <= v <= 1:
                raise forms.ValidationError(
                    'Rate must be between 0 and 1')
        if data_list and (data_list[1] < data_list[0]):
            raise forms.ValidationError(
                'Lower bound must not exceed upper bound.')
        return data_list

class EmptyChoiceField(forms.ChoiceField):
    def __init__(self, choices=(), empty_label=None, required=True, widget=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):

        # prepend an empty label if it exists (and field is not required!)
        if not required and empty_label is not None:
            choices = tuple([(u'', empty_label)] + list(choices))

        super(EmptyChoiceField, self).__init__(choices=choices, required=required, widget=widget, label=label,
            initial=initial, help_text=help_text, *args, **kwargs)

'''
class EnrollmentRange(IntegerRange):
    def compress(self, data_list):
        super(EnrollmentRange, self).compress(data_list)
        for v in data_list:
            if not 1 <= v <= 1000:
                raise forms.ValidationError(
                    'Enrollment bounds must be in the range 1 to 1000.')
        if data_list and (data_list[1] < data_list[0]):
            raise forms.ValidationError(
                'Lower bound must not exceed upper bound.')
        return data_list


class TimeRange(IntegerRange):
    def compress(self, data_list):
        super(TimeRange, self).compress(data_list)
        for v in data_list:
            if not _valid_military_time(v):
                raise forms.ValidationError(
                    'The value {:04} is not a valid military time.'.format(v))
        if data_list and (data_list[1] < data_list[0]):
            raise forms.ValidationError(
                'Lower bound must not exceed upper bound.')
        return data_list
'''

RANGE_WIDGET = forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput,
                                                  forms.widgets.NumberInput))

RANGE_WIDGET_2decimal  = forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput(attrs = {"step": "0.01"}),
                                                  forms.widgets.NumberInput(attrs = {"step": "0.01"})))

RANGE_WIDGET_100  = forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput(attrs = {"step": "100"}),
                                                  forms.widgets.NumberInput(attrs = {"step": "100"})))


class BuildingWalkingTime(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.ChoiceField(label='Building', choices=BUILDINGS,
                                    required=False),)
        super(BuildingWalkingTime, self).__init__(
            fields=fields,
            *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) == 2:
            if data_list[0] is None or not data_list[1]:
                raise forms.ValidationError(
                    'Must specify both minutes and building together.')
            if data_list[0] < 0:
                raise forms.ValidationError(
                    'Walking time must be a non-negative integer.')
        return data_list

class SearchForm_small(forms.Form):
    var_of_interest = forms.MultipleChoiceField(label='Similar counties based on:',
                                     choices=VAR_OF_INTEREST,
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)



class SearchForm(forms.Form):    # this is the class of the design of input part 
    '''
    Population = PopulationRange(
        label = "County Population (5-year average)",
        help_text = "median: xxx, 25% qunatile: xxx, 75% quantile: xxx",
        widget = RANGE_WIDGET,
        required = False
        )
    Num_household = PopulationRange(
        label = "Household number (5-year average)",
        help_text = "median: xxx, 25% qunatile: xxx, 75% quantile: xxx",
        widget = RANGE_WIDGET,
        required = False
        )
    '''    
    Region = EmptyChoiceField(label='Region', choices=REGION, 
        empty_label=u"---------",
        required=False)
    
    State_name = EmptyChoiceField(label='State', choices=STATES,
        empty_label=u"---------",
        required=False)

    winter_avg_temp = forms.FloatField(
        label = "LOWEST average temperature in winter",
        help_text = "winter: Dec/Jan/Feb",
        #widget = RANGE_WIDGET_2decimal,
        required = False
        )

    summer_avg_temp = forms.FloatField(
        label = "HIGHEST Average temperature in summer",
        help_text = "summer: Jun/Jul/Aug",
        #widget = RANGE_WIDGET_2decimal,
        required = False
        )

    Share_over65 = \
        EmptyChoiceField(label='Share of residents over 65-years old',
             choices=SHARE_OVER65, 
             help_text = "Percentage",
             empty_label=u"---------",
             required=False)


    aqi_good = \
        EmptyChoiceField(label='Air quality (ratio of days classied as "Very good")',
             choices=AQI, 
             help_text = "Regard this as a lower bound, e.g., 90 means >= 90%",
             empty_label=u"---------",
             required=False)
    '''
    unemp_rate = \
        EmptyChoiceField(label='Unemployment rate',
             choices=UNEMP_RATE, 
             help_text = "e.g., when choosing 0.1, it means range 0.1 - 0.2",
             empty_label=u"---------",
             required=False)

    Pov_rate = \
        EmptyChoiceField(label='Poverty rate',
             choices=POV_RATE, 
             help_text = "e.g., when choosing 0.1, it means range 0.1 - 0.2",
             empty_label=u"---------",
             required=False)
    '''

    largest_race = forms.MultipleChoiceField(label='Largest composition of race',
                                     choices=RACE,
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)

    Median_hhinc = MonetaryRange(
        label = "Household median income (5-year average)",
        help_text = "Unit: dollars",
        widget = RANGE_WIDGET_100,
        required = False
        )
    '''
    Incpc = MonetaryRange(
        label = "Per-capita median income (5-year average)",
        help_text = "Unit: dollars",
        widget = RANGE_WIDGET,
        required = False
        )
    '''
    median_rent_value = MonetaryRange(
        label = "Median rent level (5-year average)",
        help_text = "Unit: dollars",
        widget = RANGE_WIDGET_100,
        required = False
        )
    median_home_value = MonetaryRange(
        label = "Median house value level (5-year average)",
        help_text = "Unit: dollars",
        widget = RANGE_WIDGET_100,
        required = False
        )

    Share_college_ormore = \
        EmptyChoiceField(label='Share of residents with higher education',
             choices=SHARE_COLLEGE, 
             help_text = "Percentage",
             empty_label=u"---------",
             required=False)
    '''
    Hispanic_Latino_share = RateRange(
        label = "Share of Hispanic Latino residents",
        #help_text = "",
        widget = RANGE_WIDGET_2decimal,
        required = False
        )
    White_share = RateRange(
        label = "Share of White residents",
        #help_text = "Unit: dollars",
        widget = RANGE_WIDGET_2decimal,
        required = False
        )
    Black_share = RateRange(
        label = "Share of Black residents",
        #help_text = "Unit: dollars",
        widget = RANGE_WIDGET_2decimal,
        required = False
        )
    Asian_share = RateRange(
        label = "Share of Asian residents",
        #help_text = "Unit: dollars",
        widget = RANGE_WIDGET_2decimal,
        required = False
        )
    '''
    
    '''
    aqi_bad = RateRange(
        label = "Ratio: Very unhealthy air quality (5-year average)",
        help_text = "Ratio of days classified as unhealthy day in air quality",
        widget = RANGE_WIDGET_2decimal,
        required = False
        )

    crime_rate = RateRange(
        label = "Crime rate (5-year average)",
        help_text = "Ratio of crime occurences as percentage of population",
        widget = RANGE_WIDGET_2decimal,
        required = False
        )
    '''

    '''
    query = forms.CharField(
        label='Search terms',
        help_text='e.g. mathematics',
        required=False)
    enrollment = EnrollmentRange(
        label='Enrollment (lower/upper)',
        help_text='e.g. 1 and 40',
        widget=RANGE_WIDGET,
        required=False)
    time = TimeRange(
        label='Time (start/end)',
        help_text='e.g. 1000 and 1430 (meaning 10am-2:30pm)',
        widget=RANGE_WIDGET,
        required=False)
    time_and_building = BuildingWalkingTime(
        label='Walking time:',
        help_text='e.g. 10 and RY (at most a 10-min walk from Ryerson)',
        required=False,
        widget=forms.widgets.MultiWidget(
            widgets=(forms.widgets.NumberInput,
                     forms.widgets.Select(choices=BUILDINGS))))
    dept = forms.ChoiceField(label='Department', choices=DEPTS, required=False)
    days = forms.MultipleChoiceField(label='Days',
                                     choices=DAYS,
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)
    '''
    '''
    show_args = forms.BooleanField(label='Show args_to_ui',
                                   required=False)
    '''


def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():    # if the form is valid, the class will return the value of the class to 
                               # cleaned_data

            # Convert form data to an args dictionary for find_courses
            args = {}
            lst_to_valid1 = [    # list with one argument
                "Region",
                "State_name",
                #"largest_race"
            ]

            lst_to_valid2 = [
                
                "winter_avg_temp",
                "summer_avg_temp",
                #"unemp_rate",
                #"Share_over65",
                #"Share_under18",
                #"Share_college_ormore",

                #"Population",
                #"Num_household",
                "Median_hhinc", 
                #"Incpc",
                "median_rent_value", 
                "median_home_value", 
                #"Hispanic_Latino_share",
                #"White_share",
                #"Black_share",
                #"Asian_share",
                #"Pov_rate" ,
                #"aqi_good", 
                #"aqi_bad", 
                #"crime_rate"
                ]
            lst_to_valid3 = [
                #"aqi_good",
                #"unemp_rate",
                #"Pov_rate",
                "Share_college_ormore",
                "Share_over65",
                #"Share_under18",

            ]

            lst_to_valid4 = [
                "aqi_good"
            ]

            lst_to_valid5 = [
                "largest_race"
            ]



            for v in lst_to_valid1:
                var = form.cleaned_data[v]
                if var:
                    args[v] = var

            for v in lst_to_valid2:
                var = form.cleaned_data[v]
                if v == "winter_avg_temp":
                    if var:
                        args[v] = (var, 1000)

                elif v == "summer_avg_temp":
                    if var:
                        args[v] = (-1000, var)
                else:
                    if var:
                        args[v] = (var[0], var[1])

            for v in lst_to_valid3:
                var = form.cleaned_data[v]
                if var:
                    args[v] = (float(var.split("-")[0])/100, 
                        float(var.split("-")[1])/100)
                    #args[v] = var
                    #args[v] = (0, float(var) )

            for v in lst_to_valid4:
                var = form.cleaned_data[v]
                if var:
                    args[v] = (float(var)/100, 1)

            for v in lst_to_valid5:
                var = form.cleaned_data[v]
                if var:
                    args[v] = var

            '''
            if form.cleaned_data['show_args']:
                context['args'] = 'args_to_ui = ' + json.dumps(args, indent=2)
            '''

            ## All the way up to here is just to gather information from the user
            
            try:
                res = find_counties(DF, args)
                #res = DF.columns
            except Exception as e:
                print('Exception caught')
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in find_counties:
                <pre>{}
{}</pre>
                """.format(e, '\n'.join(bt))

                res = None
    else:
        form = SearchForm()

    
    # Handle different responses of res
    if res is None:
        context['result'] = None
    elif isinstance(res, str):    # cases where the there is an error
        context['result'] = None
        context['err'] = res
        result = None
    
    else:
        result = res
        context['result'] = result
        context['num_results'] = len(result)
        #context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]

    context['form'] = form    # form is a SearchForm object
    return render(request, 'mainpage.html', context)


def get_county_detail(request,st_fips,county_fips):

    county_detail_dict = {}

    county_object = county_detail(st_fips, county_fips)

    # get the county name
    county_name = county_object.get_name(DF)
    county_detail_dict["NAME"] = county_name

    # get the table of air quality index data
    #county_detail_dict["aqi_columns"] = county_object.aqi(DF)[0]
    #county_detail_dict["aqi_table"] = county_object.aqi(DF)[1]

    county_detail_dict["temperature_viz"] = county_object.temperature_viz(DF)
    county_detail_dict["racial_distribution"] = county_object.racial_distribution(DF)
    
    county_detail_dict["type1"] = county_object.ST
    county_detail_dict["type2"] = county_object.COUNTY

    county_detail_dict["population"] = county_object.pop(DF)
    county_detail_dict["share_over65"] = county_object.share_over65(DF)
    county_detail_dict["median_home_value"] = county_object.median_home_value(DF)
    county_detail_dict["median_rent_value"] = county_object.median_rent_value(DF)
    
    county_detail_dict["airport"] = county_object.airport(DF)
    county_detail_dict["pov_rate"] = county_object.pov_rate(DF)
    county_detail_dict["unemp_rate"] = county_object.unemp_rate(DF)
    county_detail_dict["crime_rate"] = county_object.crime_rate(DF)
    
    county_detail_dict["share_college_ormore"] = county_object.share_college_ormore(DF)
    county_detail_dict["share_highschool_orless"] = county_object.share_highschool_orless(DF)
    #county_detail_dict["similar_geo"] = county_object.find_similar_counties(DF)["geo"]
    #county_detail_dict["similar_weather"] = county_object.find_similar_counties(DF)["weather"]


    # ----------------------------------------------------------------
    #context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm_small(request.GET)
        # check whether it's valid:
        if form.is_valid():    # if the form is valid, the class will return the value of the class to 
                               # cleaned_data

            # Convert form data to an args dictionary for find_courses
            args = {"var_of_interest": []}
            convertor = {
                "Geographical location": ["Latitude", "Longitude"],
                "Weather": [
                            "winter_avg_temp",
                            "summer_avg_temp",
                             ],
                "Share of 65+ residents": ["Share_over65"],
                "Median rent value": ["median_rent_value"],
                "Air Quality": ["aqi_good"]
            }

            var = form.cleaned_data["var_of_interest"]
            if var:
                for key in convertor.keys():
                    if key in var:
                        args["var_of_interest"] = args["var_of_interest"] + convertor[key]


            

            ## All the way up to here is just to gather information from the user
            
            try:
                res = county_object.find_similar_counties(DF, args)
                #res = DF.columns
            
            except Exception as e:
                pass
    else:
        form = SearchForm_small()

    
    # Handle different responses of res
    if res is None:
        county_detail_dict['result'] = None
    elif isinstance(res, str):    # cases where the there is an error
        county_detail_dict['result'] = None
        county_detail_dict['err'] = res
        result = None
    
    else:
        result = res
        county_detail_dict['result'] = result
        county_detail_dict['num_results'] = len(result)
        #context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]

    county_detail_dict['form'] = form    # form is a SearchForm object
    #return render(request, 'mainpage.html', context)
    
    


    return render(request, 'Detailpage.html', county_detail_dict)

def get_top_hhinc(request):
    hh_inc = {}
    return render(request, 'List_of_top_counties_hhinc.html', hh_inc)





