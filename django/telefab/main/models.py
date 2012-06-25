# This file uses the following encoding: utf-8

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	"""
	Represents extra data on an user
	"""
	class Meta:
		verbose_name = u"profil"
		verbose_name_plural = u"profils"
	
	user = models.ForeignKey(User, verbose_name = u"utilisateur", unique = True)
	description = models.TextField(verbose_name = u"description", blank = True)

class Event(models.Model):
	"""
	Represents an event in the FabLab: opening, session...
	"""
	class Meta:
		verbose_name = u"évènement"
		verbose_name_plural = u"évènements"
	
	start_time = models.DateTimeField(verbose_name = u"début")
	end_time = models.DateTimeField(verbose_name = u"fin")
	EVENT_CATEGORIES = (
		(0, u"Ouverture"),
		(1, u"Atelier")
	)
	EVENT_CATEGORY_IDS = ['open', 'session']
	category = models.IntegerField(verbose_name = u"type", choices = EVENT_CATEGORIES, default = 0)
	title = models.CharField(verbose_name = u"titre", max_length = 50, blank = True)
	description = models.TextField(verbose_name = u"description", blank = True)
	animators = models.ManyToManyField(User, verbose_name = u"animateurs", blank = True)
	
	def category_id(self):
		"""
		Returns the identifier of the category of this event
		"""
		if self.category is None:
			return None
		return self.EVENT_CATEGORY_IDS[self.category]
	
	def category_name(self):
		"""
		Returns the name of the category of this event
		"""
		for id, name in dict(self.EVENT_CATEGORIES).iteritems():
			if id == self.category:
				return name
		return None
	
	def display_period(self):
		"""
		String representing the event time period
		"""
		return u"De " + self.start_time.strftime(u"%H:%M") + u" à " + self.end_time.strftime(u"%H:%M")
	
	def display_title(self):
		"""
		String representing the title depending on the type
		"""
		if self.category == 0:
			if len(self.animators.all()) > 0:
				result = u"Ouvert"
			else:
				result = u"Libre-service"
		else:
			result = self.title
		return result
	
	def display_animators(self):
		"""
		String describing the animators
		"""
		if len(self.animators.all()) == 0:
			return None
		else:
			desc = u"Animateur"
			if len(self.animators.all()) > 1:
				desc = desc + "s"
			first = True
			for animator in self.animators.all():
				if first:
					sep = " : "
					first = False
				else:
					sep = ", "
				desc = desc + sep + unicode(animator)
			return desc
	
	def __unicode__(self):
		"""
		Returns a string representation
		"""
		return self.category_name() + u" du " + self.start_time.strftime(u"%d/%m/%Y %H:%M") + u" au " + self.end_time.strftime(u"%d/%m/%Y %H:%M")
	