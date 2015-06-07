from django.conf.urls import patterns, include

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from telefab.settings import MEDIA_ROOT, MEDIA_URL
from django.conf.urls.static import static
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
	(r'^materiel/fiche/(?P<equipment_id>\d+)$', 'main.views.show_equipment_sheet'), #?P = donne un nom, \d+, digit de au moins 1 digit, ajoutee groupe 20
	# Loans
	(r'^prets/nouveau/(?P<panier>\d+)$', 'main.views.edit'),
	(r'^prets/nouveau$', 'main.views.edit'),
	(r'^prets$', 'main.views.show_loans'),
	(r'^prets/tous$', 'main.views.show_all_loans'),
	(r'^prets/(?P<loan_id>\d+)/annuler/(?P<value>\d+)$', 'main.views.manage_loan', {'action': 'cancel'}),
	(r'^prets/(?P<loan_id>\d+)/confirmer/(?P<value>\d+)$', 'main.views.manage_loan', {'action': 'confirm'}),
	(r'^prets/(?P<loan_id>\d+)/retour/(?P<value>\d+)$', 'main.views.manage_loan', {'action': 'return'}),
	(r'^prets/panier/(\d+)$', 'main.views.access_panier'), # ligne ajoutee par le groupe 20
	(r'^prets/panierempty$', 'main.views.delete_panier'), # ligne ajoutee par le groupe 20
	(r'^prets/adminpanier$', 'main.views.show_panier'), # ligne ajoutee par le groupe 20
	(r'^panier/(?P<loan_id>\d+)/annuler/(?P<value>\d+)$', 'main.views.manage_panier', {'action': 'cancel'}), # ligne ajoutee par le groupe 20
	(r'^panier/(?P<loan_id>\d+)/confirmer/(?P<value>\d+)$', 'main.views.manage_panier', {'action': 'confirm'}), # ligne ajoutee par le groupe 20
	(r'^panier/(?P<loan_id>\d+)/valider/(?P<value>\d+)$', 'main.views.manage_panier', {'action': 'valid'}), # ligne ajoutee par le groupe 20
	(r'^panier/(?P<loan_id>\d+)/(?P<panier>\d+)$', 'main.views.edit'), # ligne ajoutee par le groupe 20
	(r'^panier/paniersoumis$', 'main.views.soumettre_panier'), # ligne ajoutee par le groupe 20
	(r'^panier/monpanier$', 'main.views.my_panier'), # ligne ajoutee par le groupe 20
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
) + static(MEDIA_URL, document_root=MEDIA_ROOT)
