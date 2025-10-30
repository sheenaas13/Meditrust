from django.contrib import admin
from Mainpage.models import *

# Register your models here.
admin.site.site_header = "MediTrust Administration"
admin.site.site_title = "MediTrust Admin Portal"
admin.site.index_title = "Welcome to MediTrust Admin"

admin.site.register(Category)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'mrp', 'selling_price', 'stock', 'is_available')
    filter_horizontal = ('categories', 'subcategories') 

admin.site.register(SubCategory)
# admin.site.register(Product)
admin.site.register(ProductLabel)
@admin.register(PharmacyService)
class PharmacyServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'appointment_time', 'payment_status')
    list_filter = ('payment_status', 'service')
    search_fields = ('name', 'email', 'phone')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'is_available')

admin.site.register(CustomUser)

admin.site.register(Wishlist)

admin.site.register(QuantityOption)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__username', 'product__name')
    ordering = ('-added_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user_name', 'comment', 'product__name')

admin.site.register(Order)

admin.site.register(OrderItem)

admin.site.register(ContactQuery)

admin.site.register(Subscribe)