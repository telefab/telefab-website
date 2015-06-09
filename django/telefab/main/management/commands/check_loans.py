"""
Command added to manage.py to check loans
"""
from django.core.management.base import BaseCommand, CommandError
from main.models import Loan

class Command(BaseCommand):
    help = 'Checks the loans for late returns'

    def handle(self, *args, **options):
        for loan in Loan.objects.filter(panier=0).all():
            if loan.is_late() and loan.borrower.email:
                loan.send_reminder()
