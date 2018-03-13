from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),   ## if '' is after domain/, then call views.home
    url(r'^(?P<st_fips>\d+)/(?P<county_fips>\d+)/$',
    	views.get_county_detail, name = "get_county_detail"),
    path('temp', views.get_top_temp),
    path('hhinc', views.get_top_hhinc),
    path('rent', views.get_top_rent),
    path('pov_rate', views.get_top_pov_rate),
    path('aqi', views.get_top_aqi),
    path('edu', views.get_top_edu),
    path('crime_rate', views.get_top_crime_rate),
    path('share_over65', views.get_top_share_over65),
    path('summer_temp', views.get_top_summer_temp),
    path('winter_temp', views.get_top_winter_temp),


]
