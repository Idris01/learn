from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.files.images import ImageFile
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required

from .models import User, Category, Listing, Watchlist,Bid, Comment, Winners
from .forms import ListingForm, CategoryForm, BidForm, CommentForm


def index(request):
	active_listing=Listing.objects.filter(open=True)
	try:
		# check and get listings won by the user
		# this will throw and error for anonymous user
		winners = Winners.objects.filter(user=request.user)
		won= [win for win in winners if win.listing.open==False]
		print(won)
	except:
		won=[]

	return render(request, "auctions/index.html",{'listings':active_listing, 'won':won})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
	if request.method=='GET':
		# returns and Listing creation form
		return render(request,'auctions/create_listing.html',{'form':ListingForm()})
	else:
		# gets the posted data form the form
		form=ListingForm(request.POST,request.FILES)
		if form.is_valid():
			#check if theres photo or not
			img=form.cleaned_data['photo']
			title=form.cleaned_data['title']
			starting_bid=form.cleaned_data['starting_bid']
			description=form.cleaned_data['description']
			category=form.cleaned_data['category']
			if img != None:
				#authenticate the size of the image
					img=ImageFile(img)
					if img.width>600 or img.height>600:
						return render(request,'auctions/create_listing.html',{'form':ListingForm(request.POST),'message':"maximum required image is 600x600"})
			else:
				img=category.photo
			#attempt to save the listing
			try:
				newlisting=Listing.objects.create(user=request.user,category=category, title=title,description=description, photo=img, current_price=starting_bid, starting_bid=starting_bid, open=True)
				newlisting.save()
				return HttpResponseRedirect(reverse('index'))
			except IntegrityError:
				# A listing with the same name already exists
				return render(request,'auctions/create_listing.html',{'form':ListingForm(request.POST),'message':"Listing with the same title already exist"})
		else:
			# form contains some error
			return render(request,'auctions/create_listing.html',{'form':ListingForm(request.POST),'message':"error in input"})

@login_required
@permission_required('auctions.add_category')
def create_category(request):
	if request.method=='GET':
		return render(request,'auctions/create_category.html',{'form':CategoryForm()})
	else:
		form=CategoryForm(request.POST, request.FILES)
		if form.is_valid():
			# retrieve the image
			img=form.cleaned_data['photo']
			# check for the required image size
			img=ImageFile(img)
			if img.width>400 or img.height>400:
				return render(request,'auctions/create_category.html',{'form':CategoryForm(request.POST),'message':"required image is 400x400"})
			name=form.cleaned_data['name']

			try:
				category=Category.objects.create(name=name, photo=img)
				category.save()
				return HttpResponseRedirect(reverse('category'))

			except IntegrityError:
				return render(request,'auctions/create_category.html',{'form':CategoryForm(request.POST), 'message':"Category already exist"})
		else:
			# renders the page with an error message
			return render(request,'auctions/create_category.html',{'form':CategoryForm(request.POST), 'message':"Error in input"})


def category_view(request):
	return render(request, 'auctions/category.html',{'categories': Category.objects.all()})

class ListingDetail(generic.DetailView):
	model=Listing
	context_object_name="listing"
	template_name="auctions/listing_detail.html"
	def get_context_data(self, *args, **kwargs):
		content=super(ListingDetail, self).get_context_data(**kwargs)
		# adds a bidding form to take the bidding from the user
		content['form']=BidForm()

		# add a comment form to receive the comments form user
		content['comment_form']=CommentForm()

		# retreive all comments made on this particular listing
		content['comments']=Comment.objects.filter(listing=self.object)

		try:
			# try to check if the listing is watchlisted by the user
			w=Watchlist.objects.filter(user=self.request.user).get(item=self.get_object())
			content['watchlisted']=True
		except:
			content['watchlisted']=False

		#set the winner
		try:
			winner=Winners.objects.get(listing=self.object)
			content['winner']=winner

		except:
			pass
		return content


@login_required
def watchlist(request):
	if request.method=='GET':
		return render(request, 'auctions/watchlist.html', {'listings':Watchlist.objects.filter(user=request.user)})

	else:
		id=request.POST['pk']
		status=request.POST['status']
		w=Listing.objects.get(id=id)
		if status=='ad': # add the listing to watchlist

			watch=Watchlist.objects.create(user=request.user,item=w)
			watch.save()
			return HttpResponseRedirect(reverse('listing_detail', args=[id]))

		elif status=='rm': # remove listing from watchlist
			Watchlist.objects.filter(user=request.user).get(item=w).delete()
			return HttpResponseRedirect(reverse('listing_detail', args=[id]))

		else: # status=='cl' close the listing
			# get the winner
			bid=Bid.objects.filter(listing=w).last()
			if bid:
				# try to delete subsequent winner if one exists for the same item
				try:
					Winners.objects.filter(listing=w).delete()
				except:
					pass
				# saves a new winner
				Winners.objects.create(listing=bid.listing,user=bid.user).save()
			# change the status of the listing to false since its now closed
			w.open=False
			w.save()
			return HttpResponseRedirect(reverse('listing_detail', args=[id]))


def named_category(request, pk):
	try:
		listings=Listing.objects.filter(category_id=pk,open=True);
	except:
		listings=[]
	return render(request,"auctions/named_category.html",{"listings":listings, "category":Category.objects.get(id=pk)})

@login_required
def bid(request,pk):
	if request.method=='POST':
		try:
			# check if the request is a redirection from the bid_response page
			g=request.POST['gt']
			# At this point it is certain that the request is a redirection signal
			return HttpResponseRedirect(reverse('listing_detail', args=[pk,]))
		except:
			# At this point it is certain that a bidding request is received
			 # get the listing on which the bidding is placed
			listing=Listing.objects.get(id=pk)
			#get the bid value
			form=BidForm(request.POST)
			if form.is_valid():
				price=form.cleaned_data['price']
				# check if the bid is valid
				if listing.current_price >= price:
					return render(request,'auctions/bid_response.html',{'message':' Error!!! Your bidding price is low','success':False,'pk':pk})

				#try to save the bid and update current price
				try:
					b=Bid.objects.create(user=request.user,price=price,listing=listing)
					b.save()
					listing.current_price=price
					listing.save()
					return render(request,'auctions/bid_response.html',{'message':'Bidding Successfull!!!','success':True,'pk':pk})
				except:
					return render(request,'auctions/bid_response.html',{'message':'You can only Bid once','success':False,'pk':pk})

@login_required
def comment(request, pk):
	if request.method=='POST':
		form=CommentForm(request.POST)
		listing=Listing.objects.get(id=pk)
		if form.is_valid():
			comment=Comment.objects.create(user=request.user,message=form.cleaned_data['message'],listing=listing)
			comment.save()
			return HttpResponseRedirect(reverse('listing_detail', args=[pk]))
