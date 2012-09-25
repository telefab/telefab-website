# This file uses the following encoding: utf-8 
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.template import RequestContext, Context, Template
from django.http import HttpResponse, Http404
from django.core import urlresolvers
from django.core.mail import send_mail
from models import *
from datetime import date, datetime, timedelta
from django.utils.timezone import get_default_timezone as tz
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from vobject import iCalendar
from telefab.local_settings import WEBSITE_CONFIG
from telefab.settings import SITE_URL, EMAIL_FROM

# Events

def show_events(request, year=None, month=None, day=None):
	"""
	Show the agenda page with all current events.
	The week displayed depends on the reference date
	"""
	# Configuration
	days = 7
	hour_min = 8
	hour_max = 22
	lines_per_hour = 4 
	# Select the week to display
	if year is None or int(year) == 0:
		ref_date = date.today()
	else:
		ref_date = date(int(year), int(month), int(day))
	# Redirect to monday if not already there
	if ref_date.weekday() > 0:
		ref_date = ref_date - timedelta(days=ref_date.weekday())
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
	events = Event.objects.filter(start_time__lte=last_datetime, end_time__gte=first_datetime).order_by('-category')
	# Prepare the grid of cells to display
	hours_data = []
	today = date.today()
	event_data = {}
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
					'category': None
				}	
				days_data.append(day_data)
				cell_start_time = datetime(day.year, day.month, day.day, hour, line * 60 / lines_per_hour, 0, 0, tz())
				cell_end_time = datetime(day.year, day.month, day.day, hour, (line+1) * 60 / lines_per_hour - 1, 59, 999999, tz())
				day_data['start'] = cell_start_time
				day_data['end'] = cell_end_time
				# Search all events for events in this cell
				tests = 0
				for event in events:
					tests = tests + 1
					if event.start_time < cell_end_time and event.end_time > cell_start_time:
						day_data['event'] = event
						if event in event_data:
							day_data['cell_index'] = event_data[event] + 1
						else:
							day_data['cell_index'] = 0
						event_data[event] = day_data['cell_index']
						break
	# Render
	template_data = {
		'previous_date': {'year': str(previous_date.year).rjust(4, '0'), 'month': str(previous_date.month).rjust(2, '0'), 'day': str(previous_date.day).rjust(2, '0')},
		'next_date': {'year': str(next_date.year).rjust(4, '0'), 'month': str(next_date.month).rjust(2, '0'), 'day': str(next_date.day).rjust(2, '0')},
		'hours_data': hours_data,
		'time_position': time_position
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

# Equipments

def show_equipments(request):
	"""
	Show a list of equipments available in the FabLab
	"""
	equipments = Equipment.objects.filter(quantity__gt = 0)
	# Render
	template_data = {
		'equipments': equipments,
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
	# Check if some data has been sent
	if request.POST.get("action", None) == "save":
		# Set the return date
		scheduled_return_date = request.POST.get('scheduled_return_date', '')
		try:
			scheduled_return_date = datetime.strptime(scheduled_return_date, "%d/%m/%Y").date()
		except ValueError:
			saving_errors.append(u"la date de retour est invalide")
		if scheduled_return_date < date.today():
			saving_errors.append(u"la date de retour ne peut pas être dans le passé")
		else:
			loan.scheduled_return_date = scheduled_return_date
		# Save the loan
		loan.save()
		# Browse equipments
		i = 0
		to_save = []
		to_delete = []
		bookings_count = 0
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
					if quantity <= 0 or quantity > equipment.quantity:
						saving_errors.append("il n'y a que " + str(equipment.quantity) + " exemplaire(s) de " + equipment.name)
						continue
					# Create
					bookings_count = bookings_count + 1
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
				booking.save()
			if is_new:
				# Send an email to all animators about the new request
				body = unicode(request.user.get_profile()) + u" a fait une demande de matériel au Téléfab (retour prévu le " + loan.scheduled_return_date.strftime("%d/%m/%Y") + ") :\n"
				for booking in loan.bookings.all():
					body = body + u"* " + unicode(booking.equipment)
					if booking.quantity > 1:
						body = body + " (" + unicode(booking.quantity) + ")"
					body = body + "\n"
				body = body + "\nPour voir toutes les demandes, allez ici : " + SITE_URL + urlresolvers.reverse('main.views.show_all_loans')
				for animator in UserProfile.get_animators():
					send_mail(u"[Téléfab] Demande de matériel : " + unicode(request.user.get_profile()), body, EMAIL_FROM, [animator.email])
			# Redirect
			return redirect(urlresolvers.reverse('main.views.show_loans'))
	# Render
	template_data = {
		'loan': loan,
		'is_new': is_new,
		'is_owner': is_owner,
		'equipments': Equipment.objects.filter(quantity__gt = 0),
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
	return render_to_response("account/welcome.html", context_instance = RequestContext(request))

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