from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.urls import reverse
import datetime

class User(AbstractUser):
    pass

class Listing(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	title=models.CharField(max_length=225, unique=True)
	starting_bid=models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Starting Bid ($)')
	description=models.TextField(blank=False)
	photo=models.ImageField(upload_to='listing', blank=True, help_text="max img size 600 x 600")
	post_time=models.DateTimeField(default=timezone.now)
	category=models.ForeignKey('Category', on_delete=models.CASCADE)
	open=models.BooleanField(default=False)
	current_price=models.DecimalField(max_digits=9, decimal_places=2,default=0, help_text="current price of Listing during auction")
	def __str__(self):
		return self.title
	def get_absolute_url(self):
		return reverse('listing_detail',args=[self.id,])

class Bid(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	listing=models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="bids")
	price=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


	def __str__(self):
		return f'{self.user} bid for {self.listing} @ ${self.price}'

class Comment(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	message=models.TextField(blank=False)
	post_time=models.DateTimeField(default=datetime.datetime.now)
	listing=models.ForeignKey(Listing, on_delete=models.CASCADE)

	def __str__(self):
		return self.message
class Category(models.Model):
	name=models.CharField(max_length=225, verbose_name='Title of category', unique=True)
	photo=models.ImageField(upload_to='category', help_text="400x400 px required")

	def __str__(self):
		return self.name
class Watchlist(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,related_name="watchlists")
	item=models.ForeignKey(Listing, on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.user} watching {self.item}"
class Winners(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner")
	listing=models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="winner")

	def __str__(self):
		return f'{self.user} won {self.listing} at ${self.listing.current_price}'
