from django.conf.urls import patterns, url
from app import views
from task import views as t_view
#from  notice import  views as n_views

urlpatterns = patterns('',
                       # url(r'^$', views.index, name='index'),
                       # url(r'^test/$', t_view.created_task),
                       url(r'^login/$', views.user_login),
                       url(r'^logout/$', views.user_logout),
                       url(r'^change_password/$', views.change_password),
)