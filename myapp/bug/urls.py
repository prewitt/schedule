__author__ = 'Maple'

from django.conf.urls import patterns, url
from bug import views

urlpatterns = patterns('',
                       url(r'^add_bug/$', views.add_bug),
                       url(r'^created_bug/$', views.created_bug),
                       url(r'^add_comment/p1(\w+)p2(.+)p3(.+)/$', views.add_comment),
                       url(r'^schedule/p1(\w+)p2(.+)/$', views.add_schedule),
                       url(r'^del_bug/(.+)/$', views.del_bug),
                       url(r'^edit_bug/(.+)/$', views.edit_bug),
                       url(r'^details_bug/(.+)/$', views.details_bug),
                       url(r'^execute_bug/$', views.execute_bug),
                       url(r'^principal_bug/$', views.principal_bug),
                       url(r'^all_bug/$', views.all_bug),
                       url(r'^checked/(.+)/$', views.checked),
                       url(r'^affirm/(.+)/$', views.affirm),
                       url(r'^submit/(.+)/$', views.submit),
                       url(r'^get_comments/(?P<bug_id>\d+)/$', views.get_comments),
                       url(r'^get_feedbacks/(?P<bug_id>\d+)/$', views.get_feedbacks),
)