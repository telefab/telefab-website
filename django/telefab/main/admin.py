# This file uses the following encoding: utf-8 

from django.contrib import admin
from models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

# User administration
class UserProfileInline(admin.StackedInline):
	model = UserProfile
	max_num = 1
	can_delete = False

class UserAdmin(AuthUserAdmin):
	inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Events administration
class EventAdmin(admin.ModelAdmin):
	model = Event
	list_display = ('category', 'title', 'start_time', 'end_time')
	list_filter = ('category',)
	search_fields = ('title', 'description')
	date_hierarchy = 'start_time'
	filter_horizontal = ('animators',)
admin.site.register(Event, EventAdmin)

# Equipments administration
class EquipmentAdmin(admin.ModelAdmin):
	model = Equipment
	list_display =('name', 'quantity')
	search_fields = ('name', 'description')
admin.site.register(Equipment, EquipmentAdmin)

# EquipmentLoan inline administration (equipment in loans)
class EquipmentLoanAdmin(admin.TabularInline):
	model = EquipmentLoan

# Loan administration
class LoanAdmin(admin.ModelAdmin):
	model = Loan
	list_display = ('borrower_display', 'is_waiting', 'is_away', 'is_returned', 'scheduled_return_date')
	inlines = [EquipmentLoanAdmin,]
admin.site.register(Loan, LoanAdmin)