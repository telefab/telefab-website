# This file uses the following encoding: utf-8 
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied, ValidationError
from django.template import RequestContext, Context, Template
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from urllib.parse import urljoin, urlencode
from .models import *
from .forms import *
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django_cas_ng.views import LoginView as cas_login
from telefab.local_settings import WEBSITE_CONFIG, API_PASSWORD
from telefab.settings import SITE_URL, EMAIL_FROM, MAIN_PLACE_NAME, URL_ROOT, CAS_SERVER_URL
import math

def get_or_post(request):
	"""
	Return the GET or POST dict depending on the used method
	"""
	if request.method == "POST":
		return request.POST
	return request.GET

@login_required
def edit_event(request, event_id=None):
	"""
	Create or edit an event
	"""
	# Only animators allowed
	if not request.user.profile.is_animator():
		raise PermissionDenied()
	# Get the event to edit or create a new event
	event = None
	is_new = False
	saving_errors = []
	if event_id is not None:
		event = get_object_or_404(Event, pk=event_id)
	else:
		event = Event()
		is_new = True
	# Render
	template_data = {
		'event': event,
		'is_new': is_new,
		'saving_errors': saving_errors,
		'hours': range(24)
	}
	return render(request, "events/edit.html", template_data)

# Equipments

def show_equipment_categories(request, choice=False):
	"""
	Shows the list of equipment categories,
	used as modal dialog if choice is true
	"""
	categories = EquipmentCategory.objects.order_by('name')
	# Render
	template_data = {
		'categories': categories,
		'choice': choice
	}
	return render(request, "equipments/categories.html", template_data)

def show_equipments(request, category=None, choice=False):
	"""
	Show a list of equipments available in the FabLab (filtered by category if not None),
	used as modal dialog if choice is true
	"""
	category_obj = None
	equipments = Equipment.objects.filter(quantity__gt = 0).order_by('name')
	if category is not None:
		category_obj = get_object_or_404(EquipmentCategory, slug = category)
		equipments = equipments.filter(category = category_obj)
	
	# Render
	template_data = {
		'category': category_obj,
		'equipments': equipments,
		'choice': choice
	}
	return render(request, "equipments/show.html", template_data)


def show_equipment_sheet(request, equipment_id):
	
	equipment=get_object_or_404(Equipment, id=equipment_id)
	
	template_data = {
		'equipment': equipment,
		'error': 0
	}
	return render(request, "equipments/sheet.html", template_data)

# Rajouté par le groupe 20

def my_panier(request):
		loans = request.user.loans.filter(cancel_time = None, return_time = None, panier=1)
		error=0
		if len(loans)==0:
			error=2
		template_data = {
		'error' : error,
		'loans': loans,
		}
		return render(request, "loans/panier.html", template_data)

def access_panier(request, equipment_id):

	equipment=get_object_or_404(Equipment, id=equipment_id)

	a=int(request.POST.get("available_quantity"))
	b=int(request.POST.get("quantity"))

	if b > a or b<=0: # Vérifie que la quantité demandée est inférieure à la quantité disponible de l'équipment et est positive
		template_data = {
		'quantity': request.POST.get("quantity"),
		'available_quantity': equipment.available_quantity,
		'equipment': equipment,
		'error': 1
		}
		return render(request, "equipments/sheet.html", template_data)

	else:
		if request.user.is_authenticated: # La personne accède à son panier si elle est identifiée
			
			if Loan.objects.filter(borrower_id = request.user.id ,panier = 1, cancel_time= None): # si le panier existe déjà, on y ajoute du matériel

				emprunt = Loan.objects.filter(borrower_id = request.user.id ,panier = 1, cancel_time = None).get()
				equipment_emprunt = EquipmentLoan.objects.filter(loan = emprunt)
				flag=0
				
				# la boucle sert à vérifier si un l'équipment demandé est déjà dans le panier
				for equipment_ in equipment_emprunt: # equipment_ est un objet de type "equipmentloan"
					if equipment_.equipment.id == equipment.id:
						if (equipment_.quantity + b) > a: # on vérifie si la quantité dans le panier + celle demandée et supérieure à la quantité disponible
							template_data = {
							'quantity': b,
							'quantity_total': equipment_.quantity,
							'available_quantity': equipment.available_quantity,
							'equipment': equipment,
							'error': 2
							}
							return render(request, "equipments/sheet.html", template_data)
						else: # s'il n'y a pas d'erreur on modifie convenablement le panier
							equipment_.quantity = equipment_.quantity + b
							flag=1
							equipment_.save()
				if flag ==0: # si on a déjà modifié le panier, on ne veut pas le remodifier (flag=1)
					emprunt_equipment = EquipmentLoan()
					emprunt_equipment.equipment = equipment
					emprunt_equipment.loan = emprunt
					emprunt_equipment.quantity = request.POST.get("quantity")
					emprunt_equipment.save()
		
			else: # si le panier n'existe pas, on le crée
				emprunt = Loan()
				emprunt.borrower_id = request.user.id
				emprunt.loan_time= datetime.now()
				emprunt.panier = 1
				emprunt.save()
				# puis on remplit le panier
				emprunt_equipment = EquipmentLoan()
				emprunt_equipment.equipment = equipment
				emprunt_equipment.loan = emprunt
				#emprunt_equipment.loan = Loan.objects.get(borrower_id= request.user.id ,panier = 1)
				emprunt_equipment.quantity = request.POST.get("quantity")
				emprunt_equipment.save()


			loans = request.user.loans.filter(cancel_time = None, return_time = None, panier=1).order_by('-loan_time')
			template_data = {
			'error' : 0,
			'loans': loans,
			}
			return render(request, "loans/panier.html", template_data)

		else: # si la personne n'est pas authentifiée elle doit se connecter
			template_data = {
			'next': get_or_post(request).get('next', ''),
			}
			return render(request, "account/connection.html", template_data)

def delete_panier(request):
	# ce bout de code permet d'annuler un panier en gardant dans la BD que le panier a été annulé et non pas en faisant emprunt.delete()
	emprunt=get_object_or_404(Loan, borrower_id = request.user.id ,panier=1, cancel_time = None)
	emprunt.cancel_time = datetime.now()
	emprunt.cancelled_by = request.user
	emprunt.save()
	template_data = {
	}
	return render(request, "loans/panierempty.html", template_data)

@login_required
def show_panier(request): # Montre les paniers en cours aux administrateurs
	# Only animators
	if not request.user.profile.is_animator():
		raise PermissionDenied()

	last_time = datetime.now() - timedelta(days=7)
	loans = Loan.objects.filter(cancel_time = None, return_time = None, panier="1").exclude(scheduled_return_date = None).order_by('-loan_time')
	old_loans = Loan.objects.filter((Q(cancel_time = None) & Q(return_time__gte = last_time)) | (Q(return_time = None) & Q(cancel_time__gte = last_time))| (Q(return_time__gte = last_time) & Q(cancel_time__gte = last_time))).filter(panier="1", cancelled_by = request.user).order_by('-loan_time')

	template_data = {
	'loans': loans,
	'animator': True,
	'old_loans': old_loans,
	'error': 0
	}
	return render(request, "loans/show_panier.html", template_data)

@login_required
def manage_panier(request, loan_id, action, value):
	"""
	Allows animators to manage panier: cancel or confirm
	"""
	# Only animators
	if not request.user.profile.is_animator():
		raise PermissionDenied()
	# Detect action
	loan = get_object_or_404(Loan, pk=loan_id)
	if action == "cancel":
		# Manage the cancel status
		if value == "1":
			loan.cancel_time = datetime.now()
			loan.cancelled_by = request.user
		else:
			loan.cancel_time = None
	elif action == "valid":
		# Transforme un panier en emprunt après avoir vérifié les quantité demandés.
			emprunt = Loan.objects.filter(id = loan_id).get()
			equipment_emprunt = EquipmentLoan.objects.filter(loan = emprunt)
			for equipment_ in equipment_emprunt: # equipment_ est un objet de type "equipmentloan"
				if equipment_.equipment.available_quantity() < equipment_.quantity: # Vérifie que la quantité demandée dans le panier est bien disponible : si on rentre dans le if, il y a eu une erreur
					
					# Ces données sont nécessaires pour réafficher la même page avec un message d'erreur en cas de problème dans les quantités demandées
					last_time = datetime.now() - timedelta(days=7)
					loans = Loan.objects.filter(cancel_time = None, return_time = None, panier="1").exclude(scheduled_return_date = None).order_by('-loan_time')
					old_loans = Loan.objects.filter((Q(cancel_time = None) & Q(return_time__gte = last_time)) | (Q(return_time = None) & Q(cancel_time__gte = last_time))| (Q(return_time__gte = last_time) & Q(cancel_time__gte = last_time))).filter(panier="1", cancelled_by = request.user).order_by('-loan_time')

					template_data = {
					'loans': loans,
					'animator': True,
					'old_loans': old_loans,
					'error': 1,
					'equipment': equipment_.equipment
					}
					return render(request, "loans/show_panier.html", template_data)
			loan.panier = 0
			loan.lender = request.user
	else:
		return HttpResponseNotFound()
	loan.save()
	return redirect(reverse('main.views.show_panier'))

def soumettre_panier(request):
	now = datetime.now()
	date = request.POST.get("scheduled_return_date")

	# On vérifie ici si la date rensiengnée pour l'emprunt est valide
	error = 1
	if int(len(request.POST.get("scheduled_return_date")))==10: # 10 caractères dans aaaa-mm-jj
		if request.POST.get("scheduled_return_date")[4:5]=="-" and request.POST.get("scheduled_return_date")[7:8]=="-":# on regarde la syntaxe
			if int(request.POST.get("scheduled_return_date")[0:4]) >= now.year and int(request.POST.get("scheduled_return_date")[0:4]) <= now.year+3: #on bloque à 3 ans
				if 1 <= int(request.POST.get("scheduled_return_date")[5:7]) and int(request.POST.get("scheduled_return_date")[5:7]) <= 12:#mois compris entre 1 et 12
					if 1 <= int(request.POST.get("scheduled_return_date")[8:10]) and int(request.POST.get("scheduled_return_date")[8:10]) <= 31: #jour compris entre 1 et 31
						if now.year < int(request.POST.get("scheduled_return_date")[0:4]):# on ne regarde pas les mois et les jours, il s'agit de l'an prochain
							error = 0
						else:
							if now.month < int(request.POST.get("scheduled_return_date")[5:7]): #on ne regarde pas les jours il s'agit du mois prochain
								error = 0
							else:
								if now.day < int(request.POST.get("scheduled_return_date")[8:10]):
									error = 0
			
	#renvoi error = 1 si la date est fausse et error = 0 si elle est bonne
	if error == 1:
		loans = request.user.loans.filter(cancel_time = None, return_time = None, panier=1).order_by('-loan_time')
		template_data = {
		'loans': loans,
		'nom': request.user.username,
		'error' : 1
		}
		return render(request, "loans/panier.html", template_data)
	if error == 0:
		emprunt = Loan.objects.get(borrower_id= request.user.id ,panier = 1, cancel_time = None)
		emprunt.scheduled_return_date = request.POST.get("scheduled_return_date")
		emprunt.comment = request.POST.get("comment")
		emprunt.save()
		template_data = {}

		# Déconnecte l'utilisateur
		auth_method = request.session.get('auth_method', None)
		# Forget the login method
		try:
			del request.session['auth_method']
		except KeyError:
			pass
		auth.logout(request)
		# Log out from CAS if needed
		return render(request, "loans/panier_soumis.html", template_data)
	

@login_required
def edit(request, loan_id=None, panier=1): # Modifie les paniers et les prets suivant la valeur de "panier" reçue
	"""
	Allows users to edit a panier
	"""
	# Only animators
	if not request.user.profile.is_animator():
		raise PermissionDenied()
	# Get the loan to edit or create a new loan
	loan = None
	is_new = False
	saving_errors = []
	if loan_id is not None:
		loan = get_object_or_404(Loan, pk=loan_id)
	else:
		loan = Loan()
		loan.loan_time = datetime.now()
		is_new = True
	# Check if some data has been sent
	if request.POST.get("action", None) == "save":
		# Set the return date
		scheduled_return_date = request.POST.get('scheduled_return_date', '')
		try:
			scheduled_return_date = datetime.strptime(scheduled_return_date, "%d/%m/%Y").date()
		except ValueError:
			scheduled_return_date = None
			saving_errors.append(u"la date de retour est invalide")
		if scheduled_return_date is not None:
			if scheduled_return_date < date.today():
				saving_errors.append(u"la date de retour ne peut pas être dans le passé")
			else:
				loan.scheduled_return_date = scheduled_return_date
		# Set the comment
		loan.comment = request.POST.get('comment', '')
		# Browse equipments
		i = 0
		to_save = []
		to_delete = []
		bookings_count = 0
		equipments = []
		if not is_new:
			equipments = list(loan.equipments.all())
		while request.POST.get("equipment_id" + str(i+1), None) is not None:
			i = i + 1
			try:
				booking_id = int(request.POST.get("equipment_booking_id" + str(i), ""))
			except ValueError:
				booking_id = 0
			booking = None
			if booking_id != 0:
				try:
					booking = loan.bookings.get(pk = booking_id)
				except Booking.DoesNotExist:
					saving_errors.append(u"une réservation modifiée n'existe pas")
					continue
			remove_request = False
			try:
				remove_request = int(request.POST.get("equipment_remove" + str(i), "0")) > 0
			except:
				pass
			if remove_request:
				# This booking has been deleted
				if booking is not None:
					to_delete.append(booking)
					equipments.remove(booking.equipment)
			else:
				try:
					quantity = int(request.POST.get("equipment_quantity" + str(i), ""))
				except ValueError:
					quantity = 0
				if booking is not None:
					bookings_count = bookings_count + 1
					# This booking exists: edit the quantity
					if quantity <= 0 or quantity > booking.equipment.available_quantity(loan):
						saving_errors.append(u"il n'y a que " + str(booking.equipment.available_quantity(loan)) + " exemplaire(s) de " + booking.equipment.name)
						continue
					if quantity != booking.quantity:
						booking.quantity = quantity
						to_save.append(booking)
				else:
					# New booking
					# Get the equipment
					equipment_id = -1
					try:
						equipment_id = int(request.POST.get("equipment_id" + str(i), ""))
					except ValueError:
						pass
					if equipment_id == 0:
						# If the equipment id is 0, this is an empty field to ignore
						continue
					# Count this booking (if error, saving won't end)
					bookings_count = bookings_count + 1
					try:
						equipment = Equipment.objects.get(pk = int(request.POST.get("equipment_id" + str(i), "")))
					except (Equipment.DoesNotExist, ValueError):
						saving_errors.append(u"l'équipement \"" + request.POST.get("equipment_name" + str(i), "") + "\" n'existe pas")
						continue
					# Check that this equipment is not already booked
					if equipment in equipments:
						saving_errors.append(u"pour réserver plusieurs exemplaires d'un équipement, utilisez le champ \"quantité\"")
						continue
					# Check the quantity
					if quantity <= 0 or quantity > equipment.available_quantity(loan):
						saving_errors.append("il n'y a que " + str(equipment.available_quantity(loan)) + " exemplaire(s) de " + equipment.name)
						continue
					# Create
					booking = EquipmentLoan(loan = loan, equipment = equipment, quantity = quantity)
					to_save.append(booking)
					equipments.append(equipment)
		# Check that there is at least 1 booking
		if bookings_count == 0:
			saving_errors.append(u"au moins un équipement doit être réservé")
		# Check data about the borrower
		borrower = None
		username = request.POST.get("borrower_username", None)
		if username is None:
			saving_errors.append("Merci d'indiquer le nom d'utilisateur de l'emprunteur")
		try:
			borrower = User.objects.get(username = username)
		except User.DoesNotExist:
			email = request.POST.get("borrower_email", None)
			if email is None:
				saving_errors.append("Merci d'indiquer l'adresse électronique de l'emprunteur")
			borrower = User(username = username, email = email)
			borrower.set_unusable_password()
			try:
				borrower.full_clean()
			except ValidationError as e:
				saving_errors.append("L'adresse électronique de l'emprunteur est invalide (" + str(e) + ")")
		# Save all if no error
		if not saving_errors:
			borrower.save()
			loan.borrower_id = borrower.id
			loan.save()
			for booking in to_delete:
				booking.delete()
			for booking in to_save:
				booking.loan_id = loan.id
				booking.save()
			# Send an email for new loans
			if is_new and borrower.email:
				loan.send_reminder()
			# Redirect
			if int(panier) == 1:
				return redirect(reverse('main.views.show_panier'))
			elif int(panier) ==0:
				return redirect(reverse('main.views.show_all_loans'))
	# Render
	all_equipments = Equipment.objects.filter(quantity__gt = 0)
	equipments = []
	for equipment in all_equipments:
		# Filter out unavailable equipments
		if equipment.available_quantity(loan) > 0:
			equipments.append({
				'object': equipment,
				'quantity': equipment.available_quantity(loan)
			})
	users = User.objects.all()
	template_data = {
		'loan': loan,
		'is_new': is_new,
		'equipments': equipments,
		'users': users,
		'saving_errors': saving_errors,
		'panier': int(panier),
	}
	return render(request, "loans/edit.html", template_data)

# Fin du rajout

# Equipment loans

@login_required
def show_loans(request):
	"""
	Show all the current loans of an user
	"""
	# Loans finished less than 7 days ago, MODIF GROUPE 20 : on affiche que ceux avec panier!=1, les emprunts réalisés, pas les paniers non validés
	last_time = datetime.now() - timedelta(days=7)
	loans = request.user.loans.filter(cancel_time = None, return_time = None).order_by('-loan_time')
	old_loans = request.user.loans.filter((Q(cancel_time = None) & Q(return_time__gte = last_time)) | (Q(return_time = None) & Q(cancel_time__gte = last_time))| (Q(return_time__gte = last_time) & Q(cancel_time__gte = last_time))).order_by('-loan_time')
	template_data = {
		'loans': loans,
		'old_loans': old_loans
	}
	return render(request, "loans/show.html", template_data)

@login_required
def show_all_loans(request):
	"""
	Show all loans to animators
	"""
	# Only animators
	if not request.user.profile.is_animator():
		raise PermissionDenied()
	# Loans finished less than 7 days ago
	last_time = datetime.now() - timedelta(days=7)
	loans = Loan.objects.filter(cancel_time = None, return_time = None).exclude(panier="1").order_by('-loan_time') # exclude(panier="1") pour ne pas afficher les paniers, n'affiche pas les emprunts ayant panier = NULL.
	old_loans = Loan.objects.filter((Q(cancel_time = None) & Q(return_time__gte = last_time)) | (Q(return_time = None) & Q(cancel_time__gte = last_time))| (Q(return_time__gte = last_time) & Q(cancel_time__gte = last_time))).exclude(panier="1").order_by('-loan_time')
	template_data = {
		'loans': loans,
		'old_loans': old_loans,
		'animator': True
	}
	return render(request, "loans/show.html", template_data)

@login_required
def manage_loan(request, loan_id, action, value):
	"""
	Allows animators to manage loans: cancel or confirm
	"""
	# Only animators
	if not request.user.profile.is_animator():
		raise PermissionDenied()
	# Detect action
	loan = get_object_or_404(Loan, pk=loan_id)
	if action == "cancel":
		# Manage the cancel status
		if value == "1":
			loan.cancel_time = datetime.now()
			loan.cancelled_by = request.user
		else:
			loan.cancel_time = None
	elif action == "return":
		# Manage the return status
		if value == "1":
			loan.return_time = datetime.now()
		else:
			loan.return_time = None
	else:
		return HttpResponseNotFound()
	loan.save()
	return redirect(reverse('main.views.show_all_loans'))

# Account

@login_required
def welcome(request):
	"""
	Welcome page of the lab
	"""
	# If the user has not filled its profile: ask (only once)
	if (not request.user.first_name or not request.user.last_name or not request.user.email) and not request.session.get("already_welcome", False):
		request.session["already_welcome"] = True
		return redirect(reverse('main.views.profile') + "?first_edit=1")
	template_data = {
		'telefab_open': Place.get_main_place().now_open,
		'api_password': API_PASSWORD
	}
	return render(request, "account/welcome.html", template_data)

def connection(request):
	"""
	Default page to log in
	"""
	if request.user.is_authenticated:
		return redirect(reverse('main.views.welcome'))
	else:
		template_data = {
			'next': get_or_post(request).get('next', '')
		}
		return render(request, "account/connection.html", template_data)

def local_connection(request):
	"""
	Allows to log in locally
	"""
	error = False
	if request.user.is_authenticated:
		return redirect(reverse('main.views.welcome'))
	# Remember the login method
	request.session['auth_method'] = 'local'
	if request.method == 'POST':
		user = auth.authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
		if user is not None and user.is_active:
			auth.login(request, user)
			return redirect(reverse('main.views.welcome'))
		else:
			error = True
	template_data = {
		'error': error,
		'next': get_or_post(request).get('next', '')
	}
	return render(request, "account/local_connection.html", template_data)

def cas_connection(request):
	"""
	Allows to log in using CAS
	"""
	if request.user.is_authenticated:
		return redirect(reverse('main.views.welcome'))
	# Remember the login method
	request.session['auth_method'] = 'CAS'
	return cas_login(request)

@login_required
def logout(request):
	"""
	Log out from CAS and locally
	"""
	auth_method = request.session.get('auth_method', None)
	# Forget the login method
	try:
		del request.session['auth_method']
	except KeyError:
		pass
	auth.logout(request)
	# Log out from CAS if needed
	if auth_method == 'CAS':
		return redirect(urljoin(CAS_SERVER_URL, 'logout') + '?' + urlencode({'service': SITE_URL + URL_ROOT}))
	else:
		return redirect(SITE_URL + URL_ROOT)

@login_required
def blog(request):
	"""
	Redirect to the right blog login page
	"""
	if request.session.get('auth_method', None) == 'CAS':
		# Persons logged in through CAS will have their WP account created automatically
		return redirect('/wp-login.php')
	else:
		# Locally logged in users will have to log in manually to WordPress
		return redirect('/wp-login.php?wp')

@login_required
def profile(request):
	"""
	Modify the user profile
	"""
	just_saved = False
	# Did the user get sent here automatically at login?
	first_edit = get_or_post(request).get('first_edit', False)
	# Get data if any
	if request.method == 'POST':
		form = ProfileForm(request.POST, instance = request.user)
		if form.is_valid():
			form.save()
			just_saved = True
			if first_edit:
				# Go home if first time
				return redirect(reverse('main.views.welcome'))
	else:
		initial = {}
		if not request.user.email:
			initial['email'] = '@telecom-bretagne.eu'
		form = ProfileForm(instance = request.user, initial = initial)

	template_data = {
		'form': form,
		'first_edit': first_edit,
		'just_saved': just_saved
	}
	return render(request, "account/profile.html", template_data)

# Announcement screens

def announcements(request):
	"""
	Page displayed on announcement screens.
	Showing latest news and status
	"""
	# Select announcements that are visible, and with the right opening setting
	current_open = 'CLOSED'
	if Place.get_main_place().now_open():
		current_open = 'OPEN'
	announcements = Announcement.objects.filter(visible = True, opening__in = ('ANY', current_open))
	# Search for the first non-naked non-permanent announcement
	first_event = -1
	counter = 0
	for announcement in announcements:
		if not announcement.naked and not announcement.permanent:
			first_event = counter
			break
		counter+= 1
	# Display
	template_data = {
		'announcements': announcements,
		'first_event': first_event
	}
	return render(request, "announcements/show.html", template_data)

# Places

@login_required
def update_place(request):
	"""
	Updates a place to switch it between open or not.
	This is quite dirty for now (only the main place is supported)
	"""
	# Only animators
	if not request.user.profile.is_animator():
		raise PermissionDenied()
	# Update the place
	place = Place.get_main_place()
	if place.now_open():
		place.do_close_now()
	else:
		place.do_open_now(request.user)
	return redirect(reverse('main.views.welcome'))

def update_place_mobile(request, password):
	"""
	Mobile page to update the place opening
	"""
	if password != API_PASSWORD:
		raise PermissionDenied()
	place = Place.get_main_place()
	user = None
	if request.user.is_authenticated:
		user = request.user
	if request.POST.get('action', None) == "switch":
		if place.now_open():
			place.do_close_now()
		else:
			place.do_open_now(user)
	template_data = {
		'place': place,
		'api_password': API_PASSWORD
	}
	return render(request, "mobile/place.html", template_data)


@csrf_exempt
def update_place_api(request):
	"""
	Update the place opening (used as API)
	"""
	# Check the hard-coded password
	if request.REQUEST.get('password', None) != API_PASSWORD:
		raise PermissionDenied()
	place = Place.get_main_place()
	# Should the place be opened or closed, or is it just a check?
	to_open = request.POST.get('open', None)
	if to_open == '1':
		place.do_open_now()
	elif to_open == '0':
		place.do_close_now()
	elif place.now_open():
		return HttpResponse("OPEN", content_type="text/plain")
	else:
		return HttpResponse("CLOSED", content_type="text/plain")
	return HttpResponse("OK", content_type="text/plain")



