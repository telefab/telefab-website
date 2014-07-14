# This file uses the following encoding: utf-8 
from django.forms import ModelForm
from django.contrib.auth.models import User

class ProfileForm(ModelForm):
	"""
	Form to fill a user profile
	"""
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']
		error_messages = {
			'email': {
				'invalid': u"L'adresse électronique n'est pas valide."
			}
		}