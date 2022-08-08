from django.contrib import admin

from .models import Bid, Category, Comment, Listing, ListingDetail, User


class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "starting_bid")
    filter_horizontal = ("categories",)
    ilter_horizontal = ("users",)

class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("listings", )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")    


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(ListingDetail)
admin.site.register(Bid)
admin.site.register(Comment)