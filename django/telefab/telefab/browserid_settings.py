"""
Settings specific to browserid
"""

def guess_username(email):
	"""
	Guess an username from an email.
	Make sure it's unique
	"""
	from django.contrib.auth.models import User
	base = email.rsplit('@', 1)[0]
	counter = 0
	username = base
	while len(User.objects.filter(username=username)) > 0:
		counter = counter + 1
		username = base + "." + str(counter)
	return username