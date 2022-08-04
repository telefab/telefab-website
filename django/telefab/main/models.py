# This file uses the following encoding: utf-8

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import get_default_timezone as tz
from telefab.local_settings import WEBSITE_CONFIG
from telefab.settings import ANIMATORS_GROUP_NAME, MAIN_PLACE_NAME, EMAIL_FROM
from django.urls import reverse
from datetime import datetime, date
from django.core.mail import send_mail

class UserProfile(models.Model):
	"""
	Represents extra data on an user
	"""
	class Meta:
		verbose_name = u"profil"
		verbose_name_plural = u"profils"
	
	user = models.OneToOneField(User, verbose_name = u"utilisateur", related_name = 'profile', on_delete = models.CASCADE)
	description = models.TextField(verbose_name = u"description", blank = True)
	
	def __str__(self):
		"""
		Returns a string representation
		"""
		if self.user.first_name:
			return self.user.first_name + u" " + self.user.last_name
		else:
			return self.user.username[0].capitalize() + ". " + self.user.username[1:].capitalize()

	def is_animator(self):
		"""
		Has this user animator rights?
		"""
		return len(self.user.groups.filter(name = ANIMATORS_GROUP_NAME)) > 0

	@staticmethod
	def get_animators():
		"""
		Return the list of all animators
		"""
		return User.objects.filter(groups__name = ANIMATORS_GROUP_NAME)


class Equipment(models.Model):
	"""
	Represents equipment available in the FabLab
	"""
	class Meta:
		verbose_name = u"équipement"
		verbose_name_plural = u"matériel"

	manufacturer = models.ForeignKey("EquipmentManufacturer", verbose_name = u"fabriquant", blank = True, null = True, on_delete = models.SET_NULL)
	category = models.ForeignKey("EquipmentCategory", verbose_name = u"type", on_delete = models.CASCADE)
	name = models.CharField(verbose_name = u"nom", max_length = 100)
	reference = models.CharField(verbose_name = u"référence", max_length = 100, blank = True)
	description = models.TextField(verbose_name = u"description", blank = True)
	quantity = models.PositiveIntegerField(verbose_name = u"quantité", default = 1)
	location = models.CharField(verbose_name = u"emplacement", max_length = 100, blank = True)
	link = models.URLField(verbose_name = u"lien", blank = True)
	datasheet = models.FileField(verbose_name = u"datasheet", upload_to = "datasheet", blank = True, null = True)
	image = models.ImageField(verbose_name = u"photo", upload_to = "equipmentpic", blank = True, null = True)

	def __str__(self):
		"""
		Returns a string representation
		"""
		return self.name
    
	def get_absolute_url(self):
		"""
		Return the public URL to this object
		"""
		return reverse("main.views.show_equipment_categories")

	def available_quantity(self, loan = None):
		"""
		Return the quantity not currently away in a loan.
		If given, the loan is ignored
		"""
		available_quantity = self.quantity
		for equipment_loan in EquipmentLoan.objects.filter(equipment = self):
			if equipment_loan.loan.is_away() and equipment_loan.loan != loan and equipment_loan.loan.panier != 1: # on ne veut pas que l'équipement des paniers fasse baisser la quantité disponible.
				available_quantity-= equipment_loan.quantity
		return available_quantity


class EquipmentManufacturer(models.Model):
	"""
	Represents a manufacturer
	"""
	class Meta:
		verbose_name = u"fabriquant"
		verbose_name_plural = u"fabriquants"

	name = models.CharField(verbose_name = u"nom", max_length = 100)

	def __str__(self):
		"""
		Returns a string representation
		"""
		return self.name

class EquipmentCategory(models.Model):
	"""
	Represents an equipment type
	"""
	class Meta:
		verbose_name = u"type de matériel"
		verbose_name_plural = u"types de matériel"

	name = models.CharField(verbose_name = u"nom", max_length = 100)
	slug = models.SlugField(verbose_name = u"permalien", max_length = 100)

	def __str__(self):
		"""
		Returns a string representation
		"""
		return self.name


class Loan(models.Model):
	"""
	Represents a loan of some equipment
	"""
	class Meta:
		verbose_name = u"prêt"
		verbose_name_plural = u"prêts"

	borrower = models.ForeignKey(User, verbose_name = u"emprunteur", related_name='loans', on_delete = models.RESTRICT)
	equipments = models.ManyToManyField(Equipment, verbose_name=u"matériel", through="EquipmentLoan", blank = True)
	comment = models.TextField(verbose_name = u"commentaire", blank = True)
	loan_time = models.DateTimeField(verbose_name = u"date du prêt", blank = True, null=True)
	lender = models.ForeignKey(User, verbose_name = u"prêteur", blank = True, null=True, related_name='validated_loans', limit_choices_to = Q(groups__name = ANIMATORS_GROUP_NAME), on_delete = models.SET_NULL)
	scheduled_return_date = models.DateField(verbose_name = u"date de retour programmée", blank = True, null=True)
	return_time = models.DateTimeField(verbose_name = u"date de retour", blank = True, null=True)
	cancel_time = models.DateTimeField(verbose_name = u"date d'annulation", blank = True, null=True)
	cancelled_by = models.ForeignKey(User, verbose_name = u"annulé par", blank = True, null=True, related_name='cancelled_loans', on_delete = models.SET_NULL)
	panier = models.PositiveIntegerField(verbose_name = u"panier", default = 0)

	def __str__(self):
		"""
		String representation of the loan
		"""
		return u"Emprunt par " + unicode(self.borrower.profile)

	def is_away(self):
		"""
		Is the equipment away?
		"""
		return self.return_time is None and self.cancel_time is None
	is_away.boolean = True
	is_away.short_description = u"en cours"

	def is_returned(self):
		"""
		Has the loan been returned?
		"""
		return self.return_time is not None
	is_returned.boolean = True
	is_returned.short_description = u"rendu"

	def is_cancelled(self):
		"""
		Has the loan been cancelled?
		"""
		return self.cancel_time is not None
	is_cancelled.boolean = True
	is_cancelled.short_description = u"annulé"

	def is_late(self):
		"""
		Should the loan already be returned and is it not reurned?
		"""
		return self.is_away() and self.scheduled_return_date < date.today()

	def send_reminder(self):
		"""
		Send an email to the borrower about this loan
		"""
		message = u"Bonjour " + unicode(self.borrower.profile) + u",\n" + u"voici le matériel que vous avez emprunté au Téléfab :\n"
		for booking in self.bookings.all():
			message+= u" * " + unicode(booking.equipment.name) + u" (x" + unicode(booking.quantity) + ")\n"
		if self.comment:
			message+= u"avec le commentaire : \"" + self.comment + u"\"\n"
		if self.is_late():
			message+= u"\nLe matériel aurait dû être rendu le " + self.scheduled_return_date.strftime("%d/%m/%Y") + u".\n"
		else:
			message+= u"\nLe matériel doit être rendu le " + self.scheduled_return_date.strftime("%d/%m/%Y") + u".\n"	
		message+= u"Pour cela, merci de prendre rendez-vous avec un animateur du Téléfab en répondant à ce courriel. " + u"Il est aussi possible de prolonger le prêt si nécessaire.\n\n" + u"À bientôt,\n" + u"Le Téléfab"
		title = ""
		if self.is_late():
			title = u"Téléfab : matériel prêté à rendre"
		else:
			title = u"Téléfab : emprunt de matériel"
		#send_mail(title, message, EMAIL_FROM, [self.borrower.email])


class EquipmentLoan(models.Model):
	"""
	Binds an equipment to a loan. Includes the number of pieces loaned
	"""
	class Meta:
		verbose_name = "équipement"
		verbose_name_plural = "matériel"
	equipment = models.ForeignKey(Equipment, verbose_name = u"équipement", on_delete = models.RESTRICT)
	loan = models.ForeignKey(Loan, related_name="bookings", on_delete = models.RESTRICT)
	quantity = models.PositiveIntegerField(verbose_name = u"quantité", default = 1)

	def __str__(self):
		"""
		String representation of the equipment loan
		"""
		return unicode(self.equipment)

class Place(models.Model):
	"""
	Place with a monitored opening state
	"""
	class Meta:
		verbose_name = "lieu"
		verbose_name_plural = "lieux"
	name = models.CharField(verbose_name = u"nom", max_length = 100)

	def current_opening(self):
		"""
		Return the current opening if any, or None
		"""
		now = datetime.now(tz())
		try:
			return self.openings.get(Q(start_time__lte=now, end_time__gt=now) | Q(start_time__lte=now, end_time=None))
		except PlaceOpening.DoesNotExist:
			return None

	def now_open(self):
		"""
		Is this place currently open?
		"""
		return self.current_opening() is not None

	def do_open_now(self, animator = None):
		"""
		Set the place as currently open, return the opening if it was sucessful or null
		"""
		if self.now_open():
			return None
		return self.openings.create(start_time = datetime.now(), animator = animator)

	def do_close_now(self, animator = None):
		"""
		Set the place as currently closed, return the opening if it was sucessful or null
		"""
		opening = self.current_opening()
		if opening is None:
			return None
		opening.end_time = datetime.now()
		opening.save()
		return opening

	def __str__(self):
		"""
		String representation
		"""
		return self.name

	@staticmethod
	def get_main_place():
		"""
		Return the main place
		"""
		return Place.objects.get(name = MAIN_PLACE_NAME)

class PlaceOpening(models.Model):
	"""
	Opening period of a place
	"""
	class Meta:
		verbose_name = "ouverture"
		verbose_name_plural = "ouvertures"

	place = models.ForeignKey(Place, verbose_name = u"lieu", related_name='openings', on_delete=models.CASCADE)
	start_time = models.DateTimeField(verbose_name = u"début")
	end_time = models.DateTimeField(verbose_name = u"fin", blank = True, null = True)
	animator = models.ForeignKey(User, verbose_name = u"animateur", blank=True, null = True, limit_choices_to = Q(groups__name = ANIMATORS_GROUP_NAME), on_delete=models.SET_NULL)
	
	def __str__(self):
		"""
		Returns a string representation
		"""
		if self.end_time is not None:
			return self.place.name + u" du " + self.start_time.astimezone(tz()).strftime(u"%d/%m/%Y %H:%M") + u" au " + self.end_time.astimezone(tz()).strftime(u"%d/%m/%Y %H:%M")
		else:
			return self.place.name + u" du " + self.start_time.astimezone(tz()).strftime(u"%d/%m/%Y %H:%M") + u" à maintenant"


class Announcement(models.Model):
	"""
	Important announcements
	"""
	class Meta:
		verbose_name = "annonce"
		verbose_name_plural = "annonces"
		ordering = ['order', '-created_at']

	title = models.CharField(verbose_name = u"titre", max_length = 100)
	description = models.TextField(verbose_name = u"description")
	visible = models.BooleanField(verbose_name = u"visible", default = True)
	naked = models.BooleanField(verbose_name = u"sans habillage", default = False)
	permanent = models.BooleanField(verbose_name = u"permanente", default = False)
	opening = models.CharField(verbose_name = u"visible si", max_length = 6, default = 'ANY', choices = (('ANY', u"Tout le temps"),('OPEN', u"Téléfab ouvert"),('CLOSED', u"Téléfab fermé")))
	order = models.PositiveIntegerField(verbose_name = u"ordre", default = 1)
	created_at = models.DateTimeField(auto_now_add=True)
    
	def get_absolute_url(self):
		"""
		Return the public URL to this object
		"""
		return reverse("main.views.announcements")

	def __str__(self):
		"""
		Returns a string representation
		"""
		return self.title
