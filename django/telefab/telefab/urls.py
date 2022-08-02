from django.contrib import admin
from django.contrib.auth.decorators import login_required
from telefab.settings import MEDIA_ROOT, MEDIA_URL
from django.conf.urls.static import static
from django.urls import path
import django_cas_ng.views
import main.views

admin.autodiscover()
# Replace the default admin login page by the site login page
admin.site.login = login_required(admin.site.login)

urlpatterns = [
	# Account
	path('', main.views.welcome, name='main.views.welcome'),
	path('connexion', main.views.connection, name='main.views.connection'),
	path('connexion_locale', main.views.local_connection, name='main.views.local_connection'),
	path('connexion_cas', main.views.cas_connection, name='main.views.cas_connection'),
	path('deconnexion', main.views.logout, name='main.views.logout'),
	path('profil', main.views.profile, name='main.views.profile'),
	path('blog', main.views.blog, name='main.views.blog'),
	# Equipments
	path('materiel/tout', main.views.show_equipments, {'choice': False}, name='main.views.show_equipments'),
	path('materiel/<slug:category>', main.views.show_equipments, {'choice': False}, name='main.views.show_equipments'),
	path('materiel', main.views.show_equipment_categories, {'choice': False}, name='main.views.show_equipment_categories'),
	path('choix/materiel/tout', main.views.show_equipments, {'choice': True}, name='main.views.show_equipments'),
	path('choix/materiel/<slug:category>', main.views.show_equipments, {'choice': True}, name='main.views.show_equipments'),
	path('choix/materiel', main.views.show_equipment_categories, {'choice': True}, name='main.views.show_equipment_categories'),
	path('materiel/fiche/<int:equipment_id>', main.views.show_equipment_sheet, name='main.views.show_equipment_sheet'),
	# Loans
	path('prets/nouveau/<int:panier>', main.views.edit, name='main.views.edit'),
	path('prets/nouveau', main.views.edit, name='main.views.edit'),
	path('prets', main.views.show_loans, name='main.views.show_loans'),
	path('prets/tous', main.views.show_all_loans, name='main.views.show_all_loans'),
	path('prets/<int:loan_id>/annuler/<int:value>', main.views.manage_loan, {'action': 'cancel'}, name='main.views.manage_loan'),
	path('prets/<int:loan_id>/confirmer/<int:value>', main.views.manage_loan, {'action': 'confirm'}, name='main.views.manage_loan'),
	path('prets/<int:loan_id>/retour/<int:value>', main.views.manage_loan, {'action': 'return'}, name='main.views.manage_loan'),
	path('prets/panier/<int:equipment_id>', main.views.access_panier, name='main.views.access_panier'),
	path('prets/panierempty', main.views.delete_panier, name='main.views.delete_panier'),
	path('prets/adminpanier', main.views.show_panier, name='main.views.show_panier'),
	path('panier/<int:loan_id>/annuler/<int:value>', main.views.manage_panier, {'action': 'cancel'}, name='main.views.manage_panier'),
	path('panier/<int:loan_id>/confirmer/<int:value>', main.views.manage_panier, {'action': 'confirm'}, name='main.views.manage_panier'),
	path('panier/<int:loan_id>/valider/<int:value>', main.views.manage_panier, {'action': 'valid'}, name='main.views.manage_panier'),
	path('panier/<int:loan_id>/<int:panier>', main.views.edit, name='main.views.edit'),
	path('panier/paniersoumis', main.views.soumettre_panier, name='main.views.soumettre_panier'),
	path('panier/monpanier', main.views.my_panier, name='main.views.my_panier'),
	# Announcements
	path('ecrans', main.views.announcements, name='main.views.announcements'),
	# Places
	path('lieu/ouverture', main.views.update_place, name='main.views.update_place'),
    # Administration
    path('admin/', admin.site.urls),
    # API
    path('api/lieu', main.views.update_place_api, name='main.views.update_place_api'),
    # Mobile
    path('mobile/ouverture/<slug:password>', main.views.update_place_mobile, name='main.views.update_place_mobile')
 ] + static(MEDIA_URL, document_root=MEDIA_ROOT)
