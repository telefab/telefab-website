# This file uses the following encoding: utf-8 

from django.contrib import admin
from .models import *
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

# EquipmentCategory administration
class EquipmentCategoryAdmin(admin.ModelAdmin):
	model = EquipmentCategory
	list_display = ('name', 'slug')
	prepopulated_fields = {'slug': ('name',)}
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
	list_display = ('borrower', 'is_away', 'is_returned', 'is_cancelled', 'scheduled_return_date')
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

# Announcement administration
class AnnouncementAdmin(admin.ModelAdmin):
	model = Announcement
	list_filter = ('visible',)
	class Media:
		js = (
			'main/js/tinymce/tinymce.min.js',
			'main/js/tinymce-config/announcement-admin.js',
		)
admin.site.register(Announcement, AnnouncementAdmin)