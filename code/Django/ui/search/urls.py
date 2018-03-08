from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),   ## if '' is after domain/, then call views.home
    url(r'^(?P<st_fips>\d+)/(?P<county_fips>\d+)/$',
    	views.get_county_detail, name = "get_county_detail"),
    path('hhinc', views.get_top_hhinc),

]
