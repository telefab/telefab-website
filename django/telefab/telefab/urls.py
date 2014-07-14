from django.conf.urls import patterns, include

from django.contrib import admin
from django.contrib.auth.decorators import login_required
admin.autodiscover()
# Replace the default admin login page by the site login page
admin.site.login = login_required(admin.site.login)

urlpatterns = patterns('',
	# Account
	(r'^$', 'main.views.welcome'),
	(r'^connexion$', 'main.views.connection'),
	(r'^connexion_locale$', 'main.views.local_connection'),
	(r'^connexion_cas$', 'main.views.cas_connection'),
	(r'^deconnexion$', 'main.views.logout'),
	(r'^profil$', 'main.views.profile'),
	(r'^blog$', 'main.views.blog'),
	# Equipments
	(r'^materiel/tout$', 'main.views.show_equipments', {'choice': False}),
	(r'^materiel/(?P<category>[-\w]+)$', 'main.views.show_equipments', {'choice': False}),
	(r'^materiel$', 'main.views.show_equipment_categories', {'choice': False}),
	(r'^choix/materiel/tout$', 'main.views.show_equipments', {'choice': True}),
	(r'^choix/materiel/(?P<category>[-\w]+)$', 'main.views.show_equipments', {'choice': True}),
	(r'^choix/materiel$', 'main.views.show_equipment_categories', {'choice': True}),
	# Loans
	(r'^prets/nouveau$', 'main.views.edit_loan'),
	(r'^prets/(?P<loan_id>\d+)$', 'main.views.edit_loan'),
	(r'^prets$', 'main.views.show_loans'),
	(r'^prets/tous$', 'main.views.show_all_loans'),
	(r'^prets/(?P<loan_id>\d+)/annuler/(?P<value>\d+)$', 'main.views.manage_loan', {'action': 'cancel'}),
	(r'^prets/(?P<loan_id>\d+)/confirmer/(?P<value>\d+)$', 'main.views.manage_loan', {'action': 'confirm'}),
	(r'^prets/(?P<loan_id>\d+)/retour/(?P<value>\d+)$', 'main.views.manage_loan', {'action': 'return'}),
	# Announcements
	(r'^ecrans$', 'main.views.announcements'),
	# Places
	(r'^lieu/ouverture$', 'main.views.update_place'),
    # Administration
    (r'^admin/', include(admin.site.urls)),
    # API
    (r'^api/lieu', 'main.views.update_place_api'),
    # Mobile
    (r'^mobile/ouverture/(?P<password>[a-zA-Z0-9]+)$', 'main.views.update_place_mobile')
)
