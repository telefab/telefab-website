from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Account
	(r'^browserid/', include('django_browserid.urls')),
	(r'^connexion', 'main.views.connection'),
	# Events
	url(r'^calendrier/$', 'main.views.show_events'),
	url(r'^calendrier/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})$', 'main.views.show_events'),
	url(r'^calendrier/ical/$', 'main.views.ical_events'),
	# Equipments
	url(r'^materiel/$', 'main.views.show_equipments'),
    # Administration
    url(r'^admin/', include(admin.site.urls)),
)
