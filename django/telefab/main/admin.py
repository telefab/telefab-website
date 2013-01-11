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
	exclude = ('auto_opening',)
admin.site.register(Event, EventAdmin)

# EquipmentCategory administration
class EquipmentCategoryAdmin(admin.ModelAdmin):
	model = EquipmentCategory
admin.site.register(EquipmentCategory, EquipmentCategoryAdmin)

# EquipmentManufacturer administration
class EquipmentManufacturerAdmin(admin.ModelAdmin):
	model = EquipmentManufacturer
admin.site.register(EquipmentManufacturer, EquipmentManufacturerAdmin)

# Equipments administration
class EquipmentAdmin(admin.ModelAdmin):
	model = Equipment
	list_display = ('name', 'manufacturer', 'category', 'quantity')
	list_filter = ('category', 'manufacturer')
	search_fields = ('name', 'description', 'reference', 'location')
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

# Place administration
class PlaceAdmin(admin.ModelAdmin):
	model = Place
admin.site.register(Place, PlaceAdmin)

# Opening administration
class PlaceOpeningAdmin(admin.ModelAdmin):
	model = PlaceOpening
admin.site.register(PlaceOpening, PlaceOpeningAdmin)