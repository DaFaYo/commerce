from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator



class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    name = models.CharField(max_length=128)

    def __str__(self):
        return f"{str(self.name)}"


class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(help_text="Add a description for the listing.")
    starting_bid = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    photo = models.URLField(max_length=500, 
        help_text="Optionally provide a URL for an image for the listing", 
        blank=True)

    active = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, blank=True, related_name="listings")     
    

    def __str__(self):
        return f"{str(self.title)}: starting bid = {str(self.starting_bid)} euro's."  


class User(AbstractUser):
     listings = models.ManyToManyField(Listing, blank=True, related_name="users")

     def __str__(self):
        return f"{str(self.username)}"  


class ListingDetail(models.Model):

    listing = models.OneToOneField(Listing, 
        on_delete=models.CASCADE,
        primary_key=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{str(self.listing.title)}: created by {str(self.created_by)} on {str(self.created_at)}."  

class Bid(models.Model):

    bid = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"bid: {str(self.bid) } by {str(self.user.username)} on {str(self.listing.title)}"

class Comment(models.Model):

    comment = models.TextField(help_text="Add a comment.")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    def __str__(self):
        return f"comment_id: {str(self.id)} by: {str(self.user.username)} on {str(self.listing.title)}"
