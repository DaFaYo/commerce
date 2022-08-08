from django.urls import path

from . import views

urlpatterns = [

    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("<int:listing_id>/details", views.details_listing, name="details_listing"),
    path("<int:listing_id>/details/close_auction", views.close_auction, name="close_auction"),
    path("whishlist/<int:listing_id>", views.update_wishlist, name="update_wishlist"),
    path("whishlist", views.wishlist, name="wishlist"),
    path("category", views.category, name="category"),
    path("listing_filtered/category/<int:category_id>", views.listing_filtered_by_category, name="filtered_listing")

]
