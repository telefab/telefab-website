from django.conf.urls import patterns, include

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Account
	(r'^browserid/', include('django_browserid.urls')),
	(r'^$', 'main.views.welcome'),
	(r'^connexion$', 'main.views.connection'),
	(r'^deconnexion$', 'main.views.disconnect'),
	(r'^profil$', 'main.views.profile'),
	# Events
	(r'^calendrier/$', 'main.views.show_events'),
	(r'^calendrier/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})$', 'main.views.show_events'),
	(r'^calendrier/ical/$', 'main.views.ical_events'),
	# Equipments
	(r'^materiel$', 'main.views.show_equipments'),
	(r'^materiel/demande_pret$', 'main.views.request_loan'),
    # Administration
    (r'^admin/', include(admin.site.urls)),
)
