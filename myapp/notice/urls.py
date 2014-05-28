__author__ = 'whiteworld'
from  django.conf.urls import patterns, url
from  notice import views
from django.views.decorators.cache import cache_page
urlpatterns = patterns('',
                       url(r'^$',views.index),
                       url(r'^get_notice/$', views.get_notice),
                       url(r'^create_notice/$', views.create_notice),
                       url(r'^detail_notice/(?P<id>\d+)/$', views.detail_notice),
                       url(r'^delete_notice/(?P<id>\d+)/$', views.delete_notice),
)