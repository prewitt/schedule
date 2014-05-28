__author__ = 'PW'
from  django.conf.urls import patterns, url
from  myCalendar import views




urlpatterns = patterns('',
                       url(r'^(\d+)/$',views.home),
                       url(r'^today/$',views.todayItems),
                       url(r'^list/$',views.showList),
                       url(r'(\d{4})/(\d{1,2})/(\d+)/$',views.calendar),
                       url(r'(\d{4})/(\d{1,2})/(\d{1,2})/(\d+)/$',views.getDayItems),
)