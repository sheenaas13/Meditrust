from django.contrib import admin
from django.urls import path
from .views import add_to_cart
from . import views
from django.contrib.auth import views as auth_views
from .views import signup_view, login_view, logout_view
urlpatterns = [
path('products/', views.product_list, name='product_list'),

path('home/',views.home,name='home'),
path('admin/', admin.site.urls),
path('',views.indexpage,name='indexpage'),
path('medicine',views.medicine,name='medicine'),
path('labtest',views.labtest,name='labtest'),
path('service/<int:service_id>/book/', views.service_booking, name='service_booking'),
path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),
path('consultdoc',views.consultdoc,name='consultdoc'),
path('cancercare',views.cancercare,name='cancercare'),
path('ayurveda',views.ayurveda,name='ayurveda'),
# path('login',views.login,name='login'),
# path('signup',views.signup,name='signup'),
path('signup/', views.signup_view, name='signup'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('profile', views.profile, name='profile'),
path('careplan', views.careplan, name='careplan'),
path('partnership', views.partnership, name='partnership'),
path('wishlist', views.wishlist, name='wishlist'),
path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
path('wishlist/delete/', views.delete_wishlist_item, name='delete_wishlist_item'),
path('cart', views.cart, name='cart'),
path('cart/add/', views.add_to_cart, name='add_to_cart'),
path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
path('product/<int:id>/', views.product_detail, name='product_detail'),
path('checkout', views.checkout, name='checkout'),
path('payment-success/', views.payment_success, name='payment_success'),
path('profile/orders/', views.ordered_items_view, name='ordered_items'),
path("service/<int:service_id>/book/", views.book_service_payment, name="service_booking"),
path('service/payment-success/', views.service_payment_success, name='service_payment_success'),
path("booking/success/<int:booking_id>/", views.booking_success, name="booking_success"),

path('product_listing', views.product_listing, name='product_listing'),

path('search/', views.search_products, name='search_products'),

path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'), 
         name='password_reset'),

    # Step 2: After sending email
path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),

    # Step 3: User sets new password
path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
     name='password_reset_confirm'),

    # Step 4: Password successfully changed
path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),

path('contact', views.contact, name='contact'),

path('subscribe/', views.subscribe_view, name='subscribe'),

path('privacy', views.privacy, name='privacy'),

path('terms', views.terms, name='terms'),
path('return', views.returnpolicy, name='return'),

path('article/', views.article, name='article'),
path('articles/filter/<slug:slug>/', views.filter_articles, name='filter_articles'),

]
