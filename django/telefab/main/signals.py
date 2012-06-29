from django.db.models.signals import post_save
from models import UserProfile
from django.contrib.auth.models import User

def createUserProfile(sender, instance, **kwargs):
    """
    Create a UserProfile object each time a User is created ; and link it.
    """
    UserProfile.objects.get_or_create(user=instance)

post_save.connect(createUserProfile, sender=User)