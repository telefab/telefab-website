from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'telefab.views.home', name='home'),
    # url(r'^telefab/', include('telefab.foo.urls')),

    # Administration
    url(r'^admin/', include(admin.site.urls)),
)
