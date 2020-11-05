from django.contrib import admin
from django.contrib.admin import ModelAdmin
from . models import User, Listing, Bid,Comment, Winners

# Register your models here.
@admin.register(User)
class UserAdmin(ModelAdmin):
	pass

@admin.register(Listing)
class ListingAdmin(ModelAdmin):
	pass
@admin.register(Bid)
class BidAdmin(ModelAdmin):
	pass

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
	pass	

@admin.register(Winners)
class WinnersAdmin(ModelAdmin):
	pass	