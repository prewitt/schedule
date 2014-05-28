__author__ = 'PW'
from  django.conf.urls import patterns, url
from  staff import views




urlpatterns = patterns('',
                       url(r'^create/$',views.create),
                       url(r'^show/$',views.show),
                       url(r'^role/$',views.role),
                       url(r'^group/$',views.group),
)