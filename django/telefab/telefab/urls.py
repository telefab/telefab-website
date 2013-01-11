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
	(r'^materiel/(?P<category>\d+)$', 'main.views.show_equipments'),
	(r'^materiel$', 'main.views.show_equipment_categories'),
	# Loans
	(r'^prets/nouveau$', 'main.views.edit_loan'),
	(r'^prets/(?P<loan_id>\d+)$', 'main.views.edit_loan'),
	(r'^prets$', 'main.views.show_loans'),
	(r'^prets/tous$', 'main.views.show_all_loans'),
	(r'^prets/(?P<loan_id>\d+)/annuler/(?P<value>\d+)$', 'main.views.manage_loan', {'action': 'cancel'}),
	(r'^prets/(?P<loan_id>\d+)/confirmer/(?P<value>\d+)$', 'main.views.manage_loan', {'action': 'confirm'}),
	(r'^prets/(?P<loan_id>\d+)/retour/(?P<value>\d+)$', 'main.views.manage_loan', {'action': 'return'}),
	# Places
	(r'^lieu/ouverture$', 'main.views.update_place'),
    # Administration
    (r'^admin/', include(admin.site.urls)),
)
