__author__ = 'whiteworld'
from  django.conf.urls import patterns, url
from  meeting import views

urlpatterns = patterns('',
                       url(r'^create_meeting/$', views.create_meeting),
                       url(r'^get_meeting/$', views.get_meeting),
                       url(r'^detail_meeting/(?P<id>\d+)/$', views.detail_meeting),
                       url(r'^delete_meeting/(?P<id>\d+)/$', views.delete_meeting),

)