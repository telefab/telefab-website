from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Events
	url(r'^calendrier/$', 'main.views.show_events'),
	url(r'^calendrier/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})$', 'main.views.show_events'),
    # Administration
    url(r'^admin/', include(admin.site.urls)),
)
