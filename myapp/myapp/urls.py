from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from filebrowser.sites import site

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myapp.views.home', name='home'),
    # url(r'^myapp/', include('myapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:

    url(r'^$','app.views.index',name='Home'),
    url(r'^app/', include('app.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^calendar/', include('myCalendar.urls')),

    url(r'^staff/', include('staff.urls')),
    url(r'^notice/', include('notice.urls')),
    url(r'^meeting/', include('meeting.urls')),
    url(r'^task/', include('task.urls')),
    url(r'^bug/', include('bug.urls')),
    url(r'^filebrowser/', include(site.urls)),
)
urlpatterns += staticfiles_urlpatterns()
