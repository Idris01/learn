from django import forms
from .models import Listing, Category, Comment

class ListingForm(forms.ModelForm):
		
	class Meta:
		model=Listing
		fields= ['title','description','starting_bid','category','photo']

class CategoryForm(forms.ModelForm):
	
	class Meta:
		model=Category
		fields=('__all__')
class BidForm(forms.Form):
	price=forms.DecimalField(max_digits=10, decimal_places=2)
	
class CommentForm(forms.ModelForm):
	
	class Meta:
		model=Comment
		fields=['message']