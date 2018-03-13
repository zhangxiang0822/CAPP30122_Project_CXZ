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
from .models import find_counties, county_detail, relax_input
import random

DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'DB')
DB_FILENAME = "database_cleaned.csv"

## then we load our main database into the controller
DF = pd.read_csv(os.path.join(DB_DIR, DB_FILENAME), encoding = 'ISO-8859-1')
NUM_REC = 15    # how many results to be shown in the recommended counties

# ===================================================================
# Prepare data or user input (e.g., dropdown bar)

def _load_column(filename, col=0):
    """Load single column from csv file."""
    with open(filename) as f:
        col = list(zip(*csv.reader(f)))[0]
        return list(col)

def _load_db_column(filename, col=0):
    """Load column from database directory."""
    return _load_column(os.path.join(DB_DIR, filename), col=col)


def _build_dropdown(options):
    """Convert a list to (value, caption) tuples."""
    return [(x, x) for x in options if x is not None]

REGION = _build_dropdown(_load_db_column('region_list.csv'))
STATES = _build_dropdown(_load_db_column('states_list.csv'))
UNEMP_RATE = _build_dropdown(_load_db_column('unemp_rate_list.csv'))
POV_RATE = _build_dropdown(_load_db_column('pov_rate_list.csv'))
SHARE_COLLEGE = _build_dropdown(_load_db_column('share_college_list.csv'))
AQI = _build_dropdown(_load_db_column('aqi_list.csv'))
SHARE_OVER65 = _build_dropdown(_load_db_column('share_over65_list.csv'))
RACE = _build_dropdown(_load_db_column('race_list.csv'))
VAR_OF_INTEREST = _build_dropdown(_load_db_column('var_list.csv'))
SHOWALL = _build_dropdown(_load_db_column('showall.csv'))


## Design the class for building user-input forms

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


class EmptyChoiceField(forms.ChoiceField):
    def __init__(self, choices=(), empty_label=None, 
                 required=True, widget=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):

        # prepend an empty label if it exists (and field is not required!)
        if not required and empty_label is not None:
            choices = tuple([(u'', empty_label)] + list(choices))

        super(EmptyChoiceField, self).__init__(choices=choices, 
            required=required, widget=widget, label=label,
            initial=initial, help_text=help_text, *args, **kwargs)

## design different type of widgets
RANGE_WIDGET = \
    forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput,
                                                  forms.widgets.NumberInput))

# progress by 0.01
RANGE_WIDGET_2decimal  = \
    forms.widgets.MultiWidget(widgets= \
        (forms.widgets.NumberInput(attrs = {"step": "0.01"}),
         forms.widgets.NumberInput(attrs = {"step": "0.01"}))
                             )
# progress by 100
RANGE_WIDGET_100  = \
    forms.widgets.MultiWidget(widgets=\
        (forms.widgets.NumberInput(attrs = {"step": "100"}),
         forms.widgets.NumberInput(attrs = {"step": "100"}))
                             )

## =================================================================================
## Design the two search form classes used in user input section of 
## main page and county detail page

class SearchForm_small(forms.Form):
    '''
    This class will construct the user input section in 
    county detail page to find similar counties
    '''
    var_of_interest = forms.MultipleChoiceField(label='Similar counties based on:',
                                     choices=VAR_OF_INTEREST,
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)



class SearchForm(forms.Form):    
    '''
    This class will construct the user input section in 
    main page to find counties
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
        label = "HIGHEST average temperature in summer",
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

    showall = forms.MultipleChoiceField(label='Recommendations',
                                     choices=SHOWALL,
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)

## ===============================================================================
## Main Functions to pass the user input to the functions in models.py
## and render the returned output to htmls
## ===============================================================================

def home(request):
    '''
    This function has two functionalities:
        1. clean/organize the user input and pass it to the models
        2. render the returned output from models to main page html
    '''
    main_context = {}
    rec = None    # recommendations on counties
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():    # if the form is valid, the class will return the value of the class to 
                               # cleaned_data
            ## organize user-input into a dictionary to pass to models
            args = {}

            # we will divide user input to different category for cleaning

            lst_to_valid1 = [    # list of vars with one argument
                "Region",
                "State_name",
            ]

            lst_to_valid2 = [    # list of vars with two bounding arguments
                "winter_avg_temp",
                "summer_avg_temp",
                "Median_hhinc", 
                "median_rent_value", 
                "median_home_value", 
                ]
            lst_to_valid3 = [    # list of vars with percentage range
                "Share_college_ormore",
                "Share_over65",
            ]

            lst_to_valid4 = [    # list of vars with only one bounding args
                "aqi_good"
            ]

            lst_to_valid5 = [    # list of vars with multiple choices
                "largest_race"
            ]

            # clean the user input
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
                        float(var.split("-")[1])/100)    # parse string to range

            for v in lst_to_valid4:
                var = form.cleaned_data[v]
                if var:
                    args[v] = (float(var)/100, 1)

            for v in lst_to_valid5:
                var = form.cleaned_data[v]
                if var:
                    args[v] = var

            whether_showall = form.cleaned_data["showall"]
            
            try:
                rec = find_counties(DF, args)
            except ValueError as e:
                pass
    else:
        form = SearchForm()    # when no search was done


    if rec is not None and len(rec) == 0:
        ## when no results were found, we call in our relax_inputfunction
        ## from models.py
        keys_list = relax_input(DF, args)
        main_context['reminder'] = keys_list
        main_context['recommendations'] = None
        
    else:
        main_context['reminder'] = None
        
        if rec is not None and len(rec) > NUM_REC:    # when there are results
            if not whether_showall:    # whether to show all results
                random_ind = random.sample(range(len(rec)), NUM_REC)
                rec = [rec[i] for i in random_ind]
        main_context['recommendations'] = rec
        
    main_context['form'] = form    
    return render(request, 'mainpage.html', main_context)


def get_county_detail(request,st_fips,county_fips):
    '''
    This function mainly renders the county details to the
    county detail webpage
    '''

    county_detail_dict = {}    # create a dictionary to pass to html
    county_object = county_detail(st_fips, county_fips, DF)    # create a county detail object

    county_detail_dict["NAME"] = county_object.name
    county_detail_dict["temperature_viz"] = county_object.temperature_viz()
    county_detail_dict["racial_distribution"] = county_object.racial_distribution()
    county_detail_dict["type1"] = county_object.ST
    county_detail_dict["type2"] = county_object.COUNTY
    county_detail_dict["population"] = county_object.pop
    county_detail_dict["share_over65"] = county_object.share_over65
    county_detail_dict["median_home_value"] = county_object.median_home_value
    county_detail_dict["median_rent_value"] = county_object.median_rent_value
    county_detail_dict["Median_hhinc"] = county_object.Median_hhinc
    county_detail_dict["airport"] = county_object.airport
    county_detail_dict["pov_rate"] = county_object.pov_rate
    county_detail_dict["unemp_rate"] = county_object.unemp_rate
    county_detail_dict["crime_rate"] = county_object.crime_rate
    county_detail_dict["share_college_ormore"] = county_object.share_college_ormore
    county_detail_dict["share_highschool_orless"] = county_object.share_highschool_orless


    # ----------------------------------------------------------------
    ## we will also build a small version search engine on the county detail page
    ## to recommend similar counties based user's input on "based on which feature to
    # to find similar counties"

    rec = None
    if request.method == 'GET':
        form = SearchForm_small(request.GET)
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
                        args["var_of_interest"] = \
                            args["var_of_interest"] + convertor[key]

            try:
                rec = county_object.find_similar_counties(args)
            except ValueError as e:
                pass
            
    else:    # case where no user input has been generated
        form = SearchForm_small()

    
    if rec is None:
        county_detail_dict['recommendations'] = None
    
    else:
        county_detail_dict['recommendations'] = rec
        
    county_detail_dict['form'] = form    # form is a SearchForm object

    return render(request, 'Detailpage.html', county_detail_dict)



def get_top_temp(request):
    temp = {}
    return render(request, 'HTML_annual_avg_temp.html', temp)

def get_top_hhinc(request):
    hh_inc = {}
    return render(request, 'HTML_Median_hhinc.html', hh_inc)

def get_top_rent(request):
    rent = {}
    return render(request, 'HTML_median_rent_value.html', rent)

def get_top_pov_rate(request):
    pov_rate = {}
    return render(request, 'HTML_Pov_rate.html', pov_rate)

def get_top_aqi(request):
    aqi = {}
    return render(request, 'HTML_aqi_good.html', aqi)

def get_top_edu(request):
    edu = {}
    return render(request, 'HTML_Share_college_ormore.html', edu)

def get_top_crime_rate(request):
    crime_rate = {}
    return render(request, 'HTML_crime_rate.html', crime_rate)

def get_top_share_over65(request):
    share_over65 = {}
    return render(request, 'HTML_Share_over65.html', share_over65)


def get_top_summer_temp(request):
    summer_temp = {}
    return render(request, 'HTML_summer_avg_temp.html', summer_temp)


def get_top_winter_temp(request):
    winter_temp = {}
    return render(request, 'HTML_winter_avg_temp.html', winter_temp)


## ===============================================================================
## ===============================================================================
## Obsolete section to store the temporarily unused data and code




