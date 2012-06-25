# This file uses the following encoding: utf-8 
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, Template
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from models import *
from datetime import date, datetime, timedelta
from django.utils.timezone import get_default_timezone as tz

# Events

def show_events(request, year=None, month=None, day=None):
	"""
	Show the agenda page with all current events.
	The week displayed depends on the reference date
	"""
	# Configuration
	days = 7
	hour_min = 8
	hour_max = 18
	lines_per_hour = 4 
	# Select the week to display
	if year is None or int(year) == 0:
		ref_date = date.today()
	else:
		ref_date = date(int(year), int(month), int(day))
	# Go to monday
	ref_date = ref_date - timedelta(days=ref_date.weekday())
	# List the days
	days_range = []
	for i in range(days):
		days_range.append(ref_date + timedelta(days=i))
	first_day = days_range[0]
	last_day = days_range[-1]
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
					if event.start_time <= cell_end_time and event.end_time >= cell_start_time:
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
		'hours_data': hours_data
	}
	return render_to_response("events/show.html", template_data, context_instance = RequestContext(request))

