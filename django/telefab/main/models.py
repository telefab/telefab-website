# This file uses the following encoding: utf-8

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import get_default_timezone as tz
from telefab.local_settings import WEBSITE_CONFIG
from telefab.settings import ANIMATORS_GROUP_NAME

class UserProfile(models.Model):
	"""
	Represents extra data on an user
	"""
	class Meta:
		verbose_name = u"profil"
		verbose_name_plural = u"profils"
	
	user = models.ForeignKey(User, verbose_name = u"utilisateur", unique = True)
	description = models.TextField(verbose_name = u"description", blank = True)
	
	def __unicode__(self):
		"""
		Returns a string representation
		"""
		if self.user.first_name:
			return self.user.first_name
		else:
			return self.user.username

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
	animators = models.ManyToManyField(User, verbose_name = u"animateurs", blank = True, limit_choices_to = Q(groups__name = ANIMATORS_GROUP_NAME))
	link = models.CharField(verbose_name=u"lien", max_length = 200, blank=True)
	
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
	
	def global_title(self):
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
	
	def animators_list(self):
		"""
		String describing the animators
		"""
		anims = self.animators.all()
		if len(anims) == 0:
			return None
		else:
			desc = u""
			first = True
			for animator in anims:
				if first:
					sep = u""
					first = False
				else:
					sep = u", "
				desc = desc + sep + unicode(animator.get_profile())
			return desc

	def absolute_link(self):
		"""
		The absolute link (if easy to find)
		"""
		if self.link[0] == '/':
			return WEBSITE_CONFIG["protocol"] + '://' + WEBSITE_CONFIG["host"] + WEBSITE_CONFIG["path"] + self.link
		else:
			return self.link
	
	def __unicode__(self):
		"""
		Returns a string representation
		"""
		return self.category_name() + u" du " + self.start_time.astimezone(tz()).strftime(u"%d/%m/%Y %H:%M") + u" au " + self.end_time.astimezone(tz()).strftime(u"%d/%m/%Y %H:%M")
	