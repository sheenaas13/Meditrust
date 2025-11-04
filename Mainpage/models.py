from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        'Category', 
        on_delete=models.CASCADE, 
        related_name='subcategories'
    )
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='subcategory_images/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.category.name} -> {self.name}"
    
class ProductLabel(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    description2 = models.TextField(blank=True, null=True)

    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(blank=True, null=True)

    is_hot_deal = models.BooleanField(default=False)
    come_in_minutes = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_must_haves = models.BooleanField(default=False)

    categories = models.ManyToManyField('Category', blank=True)
    subcategories = models.ManyToManyField('SubCategory', blank=True)

    image = models.ImageField(upload_to='product_images/')
    image2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image4 = models.ImageField(upload_to='product_images/', blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def rating_distribution_list(self):
        total = self.reviews.count() or 1
        return [
            (5, int(self.reviews.filter(rating=5).count() / total * 100)),
            (4, int(self.reviews.filter(rating=4).count() / total * 100)),
            (3, int(self.reviews.filter(rating=3).count() / total * 100)),
            (2, int(self.reviews.filter(rating=2).count() / total * 100)),
            (1, int(self.reviews.filter(rating=1).count() / total * 100)),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.mrp and self.selling_price:
            self.discount_percent = int(((self.mrp - self.selling_price) / self.mrp) * 100)
        super().save(*args, **kwargs)

CATEGORY_CHOICES = (
    ('consultation','Consultation'),
    ('vaccination','Vaccination'),
    ('lab_test','Lab Test'),
    ('delivery','Delivery'),
)

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} - {self.product.name}"

class PharmacyService(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='consultation')

    def get_absolute_url(self):
        return reverse('service_booking', args=[self.id])

    def __str__(self):
        return self.name

class ServiceBooking(models.Model):
    service = models.ForeignKey('PharmacyService', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    test_type = models.CharField(max_length=100, blank=True, null=True)
    appointment_time = models.DateTimeField(null=True, blank=True)
    hospital_address = models.CharField(max_length=255, default="Main Hospital")
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"{self.name} - {self.service.name} with {self.doctor}"

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True, upload_to='doctors/')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.specialty})"
    
class CustomUser(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    contact_no = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.username
    
class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product.name} (x{self.quantity})"

    @property
    def total_price(self):
        return self.product.selling_price * self.quantity
    
class QuantityOption(models.Model):
    product = models.ForeignKey(Product, related_name='quantity_options', on_delete=models.CASCADE)
    label = models.CharField(max_length=50)  # e.g. '120ml', '250ml', '500ml'

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    user_image = models.ImageField(upload_to='reviewer_images/', blank=True, null=True)  # NEW field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.product.name} ({self.rating}⭐)"
    

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    products = models.ManyToManyField('Product', through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Paid, Delivered
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
class ContactQuery(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
class Subscribe(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class ArticleCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Article Categories"

    def __str__(self):
        return self.name


class Article(models.Model):
    CATEGORY_CHOICES = [
        ('BIG', 'Featured Large Article'),
        ('SMALL', 'Small Article'),
    ]

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='articles/')
    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE, related_name="articles")
    article_type = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='SMALL')
    short_description = models.TextField()
    author = models.CharField(max_length=100, default="Admin")
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title