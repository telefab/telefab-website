# This file uses the following encoding: utf-8 
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.template import RequestContext, Context, Template
from django.http import HttpResponse, Http404
from django.core import urlresolvers
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from models import *
from datetime import date, datetime, timedelta
from django.utils.timezone import get_default_timezone as tz
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from vobject import iCalendar
from telefab.local_settings import WEBSITE_CONFIG, API_PASSWORD
from telefab.settings import SITE_URL, EMAIL_FROM, MAIN_PLACE_NAME
import math

# Events

def show_events(request, year=None, month=None, day=None):
	"""
	Show the agenda page with all current events.
	The week displayed depends on the reference date
	"""
	# Configuration
	days = 7
	hour_min = 9
	hour_max = 18
	lines_per_hour = 3
	# Select the week to display
	if year is None or int(year) == 0:
		ref_date = date.today()
	else:
		ref_date = date(int(year), int(month), int(day))
	# Redirect to monday if not already there
	if ref_date.weekday() % days > 0:
		ref_date = ref_date - timedelta(days=(ref_date.weekday() % days))
		return redirect("main.views.show_events", year=str(ref_date.year).rjust(4, '0'), month=str(ref_date.month).rjust(2, '0'), day=str(ref_date.day).rjust(2, '0'))
	# List the days
	days_range = []
	for i in range(days):
		days_range.append(ref_date + timedelta(days=i))
	first_day = days_range[0]
	last_day = days_range[-1]
	# Get the position in time of this week:
	if first_day > date.today():
		time_position = "future"
	elif last_day < date.today():
		time_position = "past"
	else:
		time_position = "present"
	# Prepare the next and previous dates
	next_date = ref_date + timedelta(days=7)
	previous_date = ref_date - timedelta(days=7)
	# Get the events to display
	first_datetime = datetime(first_day.year, first_day.month, first_day.day, 0, 0, 0, 0, tz())
	last_datetime = datetime(last_day.year, last_day.month, last_day.day, 23, 59, 59, 999999, tz())
	events = Event.objects.filter(start_time__lte=last_datetime, end_time__gte=first_datetime).order_by('start_time')
	openings = PlaceOpening.objects.filter(place=Place.get_main_place(), start_time__lte=last_datetime).filter(Q(end_time__gte=first_datetime) | Q(end_time = None)).order_by('start_time')
	# Enlarge the times if needed
	for event in events:
		if event.start_time.hour < hour_min:
			hour_min = event.start_time.hour
		if event.end_time.hour > hour_max:
			hour_max = event.end_time.hour
	# Prepare the grid of cells to display
	hours_data = []
	today = date.today()
	for hour in range(hour_min, hour_max + 1):
		lines_data = []
		hour_data = {
			'hour': hour,
			'lines': lines_data
		}	
		hours_data.append(hour_data)
		for line in range(lines_per_hour):
			days_data = []
			line_data = {
				'line': line,
				'days': days_data
			}	
			lines_data.append(line_data)
			for day in days_range:
				day_data = {
					'day': day,
					'current': day == today,
					'main_place_open': False
				}	
				days_data.append(day_data)
				cell_start_time = datetime(day.year, day.month, day.day, hour, line * 60 / lines_per_hour, 0, 0, tz())
				cell_end_time = datetime(day.year, day.month, day.day, hour, (line+1) * 60 / lines_per_hour - 1, 59, 999999, tz())
				column_end_time = datetime(day.year, day.month, day.day, hour_max, 59, 59, 999999, tz())
				day_data['start'] = cell_start_time
				day_data['end'] = cell_end_time
				# Check if the main place was open during this period
				for opening in openings:
					if opening.start_time < cell_end_time:
						if (opening.end_time is None and cell_start_time < datetime.now(tz())) or (opening.end_time is not None and opening.end_time > cell_start_time):
							day_data['main_place_open'] = True
							break
					else:
						break
				day_data['events'] = [] 
				# Search all events for events in this cell
				for event in events:
					if event.start_time >= cell_start_time and event.start_time <= cell_end_time:
						event_data = {}
						event_data['event'] = event
						# Simultaneous events?
						simult_events = 0
						simult_index = 0
						for test_event in events:
							if test_event.start_time.date() == day and test_event != event and test_event.start_time < event.end_time and test_event.end_time > event.start_time:
								simult_events = simult_events + 1
							elif test_event == event:
								simult_index = simult_events
						# Event position
						compare_time = event.end_time
						if compare_time > column_end_time:
							compare_time = column_end_time
						event_data['height'] = int(math.ceil(100. * (compare_time - event.start_time).seconds / (60 * 60 / lines_per_hour))) - 2
						event_data['top'] = int(math.ceil(100. * (event.start_time - cell_start_time).seconds / (60 * 60 / lines_per_hour)))
						event_data['width'] = int(math.ceil(100. / (simult_events + 1))) - 2
						event_data['left'] = int(math.ceil(100. * simult_index / (simult_events + 1)))
						day_data['events'].append(event_data)
	# Render
	template_data = {
		'previous_date': {'year': str(previous_date.year).rjust(4, '0'), 'month': str(previous_date.month).rjust(2, '0'), 'day': str(previous_date.day).rjust(2, '0')},
		'next_date': {'year': str(next_date.year).rjust(4, '0'), 'month': str(next_date.month).rjust(2, '0'), 'day': str(next_date.day).rjust(2, '0')},
		'hours_data': hours_data,
		'time_position': time_position,
		'telefab_open': Place.get_main_place().now_open
	}
	return render_to_response("events/show.html", template_data, context_instance = RequestContext(request))

def ical_events(request):
	"""
	Next 50 events in ical format
	"""
	calendar = iCalendar()
	calendar.add("name").value = u"Téléfab"
	for event in Event.objects.filter(end_time__gte=datetime.now()).order_by('start_time')[0:50]:
		ical_ev = calendar.add("vevent")
		ical_ev.add("uid").value = "EVENT" + str(event.id) + "@" + WEBSITE_CONFIG["host"]
		ical_ev.add("dtstart").value = event.start_time
		ical_ev.add("dtend").value = event.end_time
		ical_ev.add("summary").value = event.global_title()
		ical_ev.add("categories").value = [event.category_name()]
		ical_ev.add("location").value = event.location
		if event.description:
			ical_ev.add("description").value = event.description
		for animator in event.animators.all():
			ical_ev.add("attendee").value = unicode(animator.get_profile())
		if event.link:
			ical_ev.add("url").value = event.absolute_link()
	return HttpResponse(calendar.serialize(), mimetype="text/calendar")

@login_required
def edit_event(request, event_id=None):
	"""
	Create or edit an event
	"""
	# Only animators allowed
	if not request.user.get_profile().is_animator():
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
	return render_to_response("events/edit.html", template_data, context_instance = RequestContext(request))

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
	return render_to_response("equipments/categories.html", template_data, context_instance = RequestContext(request))

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
	return render_to_response("equipments/show.html", template_data, context_instance = RequestContext(request))

# Equipment loans

@login_required
def edit_loan(request, loan_id=None):
	"""
	Allows users to edit a loan or create one
	"""
	# Get the loan to edit or create a new loan
	loan = None
	is_new = False
	is_owner = True
	saving_errors = []
	if loan_id is not None:
		loan = get_object_or_404(Loan, pk=loan_id)
		# Check that the user can edit this loan
		if loan.borrower != request.user:
			if not request.user.get_profile().is_animator() or loan.cancel_time:
				raise PermissionDenied()
			is_owner = False
		elif not loan.is_waiting():
			raise PermissionDenied()
	else:
		loan = Loan()
		loan.borrower = request.user
		loan.request_time = datetime.now()
		is_new = True
	loan.set_editing(True)
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
					if quantity <= 0 or quantity > booking.equipment.quantity:
						saving_errors.append(u"il n'y a que " + str(booking.equipment.quantity) + " exemplaire(s) de " + booking.equipment.name)
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
					if quantity <= 0 or quantity > equipment.available_quantity():
						saving_errors.append("il n'y a que " + str(equipment.available_quantity()) + " exemplaire(s) de " + equipment.name)
						continue
					# Create
					booking = EquipmentLoan(loan = loan, equipment = equipment, quantity = quantity)
					to_save.append(booking)
					equipments.append(equipment)
		# Check that there is at least 1 booking
		if bookings_count == 0:
			saving_errors.append(u"au moins un équipement doit être réservé")
		if not saving_errors:
			# Save all if no error
			loan.save()
			for booking in to_delete:
				booking.delete()
			for booking in to_save:
				booking.loan_id = loan.id
				booking.save()
			if is_new:
				# Send an email to all animators about the new request
				body = unicode(request.user.get_profile()) + u" a fait une demande de matériel au Téléfab (retour prévu le " + unicode(loan.scheduled_return_date.strftime("%d/%m/%Y")) + u") :\n"
				for booking in loan.bookings.all():
					body = body + u"* " + unicode(booking.equipment)
					if booking.quantity > 1:
						body = body + u" (" + unicode(booking.quantity) + u")"
					body = body + "\n"
				body = body + u"\nPour voir toutes les demandes, allez ici : " + unicode(SITE_URL + urlresolvers.reverse('main.views.show_all_loans'))
				for animator in UserProfile.get_animators():
					send_mail(u"[Téléfab] Demande de matériel : " + unicode(request.user.get_profile()), body, EMAIL_FROM, [animator.email])
			# Redirect
			return redirect(urlresolvers.reverse('main.views.show_loans'))
	# Render
	all_equipments = Equipment.objects.filter(quantity__gt = 0)
	equipments = []
	for equipment in all_equipments:
		# Filter out unavailable equipments
		if equipment.available_quantity > 0:
			equipments.append(equipment)
	template_data = {
		'loan': loan,
		'is_new': is_new,
		'is_owner': is_owner,
		'equipments': equipments,
		'saving_errors': saving_errors
	}
	return render_to_response("loans/edit.html", template_data, context_instance = RequestContext(request))

@login_required
def show_loans(request):
	"""
	Show all the current loans of an user
	"""
	# Loans finished less than 7 days ago
	last_time = datetime.now() - timedelta(days=7)
	loans = request.user.loans.filter(cancel_time = None, return_time = None).order_by('-request_time')
	old_loans = request.user.loans.filter((Q(cancel_time = None) & Q(return_time__gte = last_time)) | (Q(return_time = None) & Q(cancel_time__gte = last_time))).order_by('-request_time')
	template_data = {
		'loans': loans,
		'old_loans': old_loans
	}
	return render_to_response("loans/show.html", template_data, context_instance = RequestContext(request))

@login_required
def show_all_loans(request):
	"""
	Show all loans to animators
	"""
	# Only animators
	if not request.user.get_profile().is_animator():
		raise PermissionDenied()
	# Loans finished less than 7 days ago
	last_time = datetime.now() - timedelta(days=7)
	loans = Loan.objects.filter(cancel_time = None, return_time = None).order_by('-request_time')
	old_loans = Loan.objects.filter((Q(cancel_time = None) & Q(return_time__gte = last_time)) | (Q(return_time = None) & Q(cancel_time__gte = last_time))).order_by('-request_time')
	template_data = {
		'loans': loans,
		'old_loans': old_loans,
		'animator': True
	}
	return render_to_response("loans/show.html", template_data, context_instance = RequestContext(request))

@login_required
def manage_loan(request, loan_id, action, value):
	"""
	Allows animators to manage loans: cancel or confirm
	"""
	# Only animators
	loan = get_object_or_404(Loan, pk=loan_id)
	if action == "cancel":
		# Manage the cancel status
		if (loan.borrower != request.user or loan.loan_time) and not request.user.get_profile().is_animator():
			raise PermissionDenied()
		if value == "1":
			loan.cancel_time = datetime.now()
			loan.cancelled_by = request.user
		else:
			loan.cancel_time = None
	elif action =="return":
		# Manage the return status
		if not request.user.get_profile().is_animator():
			raise PermissionDenied()
		if loan.cancel_time or not loan.loan_time:
			raise PermissionDenied()
		if value == "1":
			loan.return_time = datetime.now()
		else:
			loan.return_time = None
	elif action == "confirm":
		# Manage the confirm status
		if not request.user.get_profile().is_animator():
			raise PermissionDenied()
		if loan.cancel_time:
			raise PermissionDenied()
		if value == "1":
			loan.loan_time = datetime.now()
			loan.lender = request.user
		else:
			loan.loan_time = None
	else:
		raise Http404()
	loan.save()
	if request.user.get_profile().is_animator():
		return redirect(urlresolvers.reverse('main.views.show_all_loans'))
	else:
		return redirect(urlresolvers.reverse('main.views.show_loans'))

# Account

@login_required
def welcome(request):
	"""
	Welcome page of the lab
	"""
	# If the user has not filled its profile: ask (only once)
	if (not request.user.first_name or not request.user.last_name) and not request.session.get("already_welcome", False):
		request.session["already_welcome"] = True
		return redirect(urlresolvers.reverse('main.views.profile') + "?first_edit=1")
	template_data = {
		'telefab_open': Place.get_main_place().now_open
	}
	return render_to_response("account/welcome.html", template_data, context_instance = RequestContext(request))

def connection(request):
	"""
	Allows to register or log in
	"""
	if request.user.is_authenticated():
		return redirect(urlresolvers.reverse('main.views.welcome'))
	else:
		template_data = {
			'next': request.REQUEST.get('next', '')
		}
		return render_to_response("account/connection.html", template_data, context_instance = RequestContext(request))

def disconnect(request):
	"""
	Log the user out
	"""
	logout(request)
	return render_to_response("account/disconnect.html", context_instance = RequestContext(request))

def blog(request):
	"""
	Simple page to allow to log in on the blog.
	If the user seems to be logged in, send directly
	"""
	# Redirect users who seem logged in
	# to avoid plenty of useless redirections
	# this is not trustworthy: remove if it creates problems!
	for name in request.COOKIES:
		if name.find("wordpress_logged_in") == 0:
			return redirect('/wp-admin')
	return render_to_response("account/blog.html", context_instance = RequestContext(request))

@login_required
def profile(request):
	"""
	Modify the user profile
	"""
	# Did the user get sent here automatically at login?
	first_edit = request.REQUEST.get('first_edit', False)
	# Get data if any
	first_name = request.POST.get('first_name', None)
	last_name = request.POST.get('last_name', None)
	just_saved = False
	if first_name is not None and last_name is not None :
		request.user.first_name = first_name
		request.user.last_name = last_name
		request.user.save()
		just_saved = True
		if first_edit:
			# Go home if first time
			return redirect(urlresolvers.reverse('main.views.welcome'))
	template_data = {
		'first_edit': first_edit,
		'just_saved': just_saved
	}
	return render_to_response("account/profile.html", template_data, context_instance = RequestContext(request))

# Places

@login_required
def update_place(request):
	"""
	Updates a place to switch it between open or not.
	This is quite dirty for now (only the main place is supported)
	"""
	# Only animators
	if not request.user.get_profile().is_animator():
		raise PermissionDenied()
	# Update the place
	place = Place.get_main_place()
	if place.now_open():
		place.do_close_now()
	else:
		place.do_open_now(request.user)
	return redirect(urlresolvers.reverse('main.views.welcome'))

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