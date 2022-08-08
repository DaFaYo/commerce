from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from auctions.forms import ListingForm, NewBidForm, NewCommentForm

from .models import Bid, Category, Comment, Listing, ListingDetail, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ObjectDoesNotExist, BadRequest
from django.views.defaults import page_not_found, bad_request
from django.db.models import Count, Max


PASSWORD_MIN_LENGTH = 8
NAME_ADD_TO_WISHLIST = "Add to wishlist"
NAME_REMOVE_FROM_WISHLIST = "Remove from wishlist"


def index(request):
    return render(request, "auctions/index.html", {
       "listings": Listing.objects.all(),
       "add_to_wishlist": NAME_ADD_TO_WISHLIST,
       "remove_from_wishlist": NAME_REMOVE_FROM_WISHLIST
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user:
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
        if len(str(password)) < PASSWORD_MIN_LENGTH:
            return render(request, "auctions/register.html", {
                "message": f"Passwords must be at least {PASSWORD_MIN_LENGTH} characters long."
            })             

        # Attempt to create new user
        try:
            validate_username = UnicodeUsernameValidator()
            validate_username(username) 

            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        except ValueError as err:
            return render(request, "auctions/register.html", {
                "message": str(err)
            })    
        except ValidationError as err:
            return render(request, "auctions/register.html", {
                "message": str(err)
            })    
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@transaction.atomic
@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            
            try:
                with transaction.atomic():

                    listingObj = form.save()
                    listingDetail = ListingDetail(listing = listingObj, created_by=request.user)
                    listingDetail.save()

            except IntegrityError:
                pass

            return HttpResponseRedirect(reverse("index"))
            
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form
            })  
    return render(request, "auctions/create_listing.html", {
                "form": ListingForm()
            })



def details_listing(request, listing_id):
    listing = None
    try:

        listing = Listing.objects.get(pk=listing_id)

    except ObjectDoesNotExist as e:
        return page_not_found(request, e)    

    if not hasattr(listing, 'listingdetail'):
        return bad_request(request, BadRequest)

    non_categories = Category.objects.exclude(listings=listing).all()
    details = listing.listingdetail      
    bids_dict = Bid.objects.filter(listing=listing).aggregate(Count("bid"), Max("bid"))
    num_of_bids = bids_dict["bid__count"]
    highest_bid = bids_dict["bid__max"]

    highest_bidder = None
    bid_info_message = []
    if num_of_bids:
        bid_info_message.append(f"{num_of_bids} bid(s) so far.")
        bid  = Bid.objects.filter(listing=listing, bid=highest_bid).get()
        highest_bidder = bid.user
    else:
        bid_info_message.append("0 bid(s) so far.")

    if highest_bidder:
        if request.user and (request.user == highest_bidder):
            bid_info_message.append("Your bid is the current bid.")
        else:
            bid_info_message.append(f"{highest_bidder.username} has the highest bid.")
                
    if request.method == "POST" and request.POST["submit"] == "Place Bid":
        return handleBidding(
            request, 
            listing, 
            details, 
            highest_bid,
            non_categories
        )

    if request.method == "POST" and request.POST["submit"] == "Add comment":
        return add_comment(
            request, 
            listing, 
            details, 
            bid_info_message, 
            highest_bidder,
            non_categories
        )    
       
    return render(request, "auctions/details_listing.html", {
        "listing": listing,
        "listing_details": details,
        "bid_info_message": " ".join(bid_info_message),
        "highest_bidder": highest_bidder,
        "form": NewBidForm(),
        "comments": Comment.objects.filter(listing=listing).all(),
        "comment_form": NewCommentForm(),
        "non_categories": non_categories,
        "add_to_wishlist": NAME_ADD_TO_WISHLIST,
        "remove_from_wishlist": NAME_REMOVE_FROM_WISHLIST
    })


@login_required
def handleBidding(request, listing, details, highest_bid, non_categories):

    if (request.user == details.created_by):
         return bad_request(request, BadRequest) 

    form = NewBidForm(request.POST)
    if form.is_valid():
        new_bid = form.cleaned_data["bid"]
               
        if (new_bid < listing.starting_bid):

            return render(request, "auctions/details_listing.html", {
                "error_message": "Your bid is smaller than the starting bid",
                "listing": listing,
                "listing_details": details,
                "form": form,
                "comments": Comment.objects.filter(listing=listing).all(),
                "comment_form": NewCommentForm(),
                "non_categories": non_categories,
                "add_to_wishlist": NAME_ADD_TO_WISHLIST,
                "remove_from_wishlist": NAME_REMOVE_FROM_WISHLIST
            })

        elif highest_bid and (new_bid <= highest_bid):

            return render(request, "auctions/details_listing.html", {
                "error_message": "Your bid is smaller than the highest bid",
                "listing": listing,
                "listing_details": details,
                "form": form,
                "comments": Comment.objects.filter(listing=listing).all(),
                "comment_form": NewCommentForm(),
                "non_categories": non_categories,
                "add_to_wishlist": NAME_ADD_TO_WISHLIST,
                "remove_from_wishlist": NAME_REMOVE_FROM_WISHLIST
            })

        else:

            Bid.objects.create(bid=new_bid, user=request.user, listing=listing)
            return HttpResponseRedirect(reverse("details_listing", kwargs={ "listing_id": listing.id }))           

    else:

        return render(request, "auctions/details_listing.html", {
            "listing": listing,
            "listing_details": details,
            "form": form,
            "comments": Comment.objects.filter(listing=listing).all(),
            "comment_form": NewCommentForm(),
            "non_categories": non_categories,
            "add_to_wishlist": NAME_ADD_TO_WISHLIST,
            "remove_from_wishlist": NAME_REMOVE_FROM_WISHLIST
        })
    

@login_required
def close_auction(request, listing_id):
    if request.method == "POST" and listing_id:

        listing = Listing.objects.get(pk=listing_id)
        action = request.POST["submit"]
        if action == "Close the auction":
            listing.active = False
            listing.save()

    return redirect(request.META['HTTP_REFERER'])       


@login_required
def add_comment(request, listing, details, bid_info_message, highest_bidder, non_categories):
    form = NewCommentForm(request.POST)
    if form.is_valid():
        new_comment = form.cleaned_data["comment"]

        Comment.objects.create(comment=new_comment, user=request.user, listing=listing)
        return HttpResponseRedirect(reverse("details_listing", kwargs={ "listing_id": listing.id }))           

    else:
        return render(request, "auctions/details_listing.html", {
        "listing": listing,
        "listing_details": details,
        "bid_info_message": " ".join(bid_info_message),
        "highest_bidder": highest_bidder,
        "form": NewBidForm(),
        "comments": Comment.objects.filter(listing=listing).all(),
        "comment_form": form,
        "non_categories": non_categories,
        "add_to_wishlist": NAME_ADD_TO_WISHLIST,
        "remove_from_wishlist": NAME_REMOVE_FROM_WISHLIST
    })


@login_required
def update_wishlist(request, listing_id = None):
    if request.method == "POST" and listing_id:

        listing = Listing.objects.get(pk=listing_id)
        action = request.POST["submit"]

        if action == NAME_ADD_TO_WISHLIST:
            if request.user not in listing.users.all():
                listing.users.add(request.user)
        if action == NAME_REMOVE_FROM_WISHLIST:
            if request.user in listing.users.all():
                listing.users.remove(request.user)

    return redirect(request.META['HTTP_REFERER'])     


@login_required
def wishlist(request):
    return render(request, "auctions/wishlist.html")


def category(request):
    return render(request, "auctions/category.html", {
        "categories": Category.objects.all()
    })


def listing_filtered_by_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        listings = Listing.objects.filter(categories=category).all()  
        
        return render(request, "auctions/index.html", {
            "listings": listings,
            "add_to_wishlist": NAME_ADD_TO_WISHLIST,
            "remove_from_wishlist": NAME_REMOVE_FROM_WISHLIST
        }) 

    except ObjectDoesNotExist as e:
        return page_not_found(request, e)

