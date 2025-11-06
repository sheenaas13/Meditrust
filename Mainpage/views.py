from django.shortcuts import render, get_object_or_404, redirect
from Mainpage.models import *
from django.conf import settings
from django.core.mail import send_mail
import uuid
from datetime import datetime, timedelta
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.db.models import Q
import razorpay

def pharmacy_services(request):
    return {'pharmacy_services': PharmacyService.objects.filter(is_available=True)}

# Create your views here.
def indexpage(request):
    pharmacy_services = PharmacyService.objects.filter(is_available=True)
    categories = Category.objects.all()
    paginator = Paginator(categories, 21)  # 21 categories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    hot_deals = Product.objects.filter(is_hot_deal=True, is_available=True).order_by('-created_at')[:8]
    must_haves = Product.objects.filter(is_must_haves=True, is_available=True).order_by('-created_at')[:8]
    come_in_minutes = Product.objects.filter(come_in_minutes=True, is_available=True).order_by('-created_at')[:8]
    new_arrivals = Product.objects.filter(
        is_new_arrival=True,
        is_available=True
    ).order_by('-created_at')[:8]
    
    return render(request,'index.html',{'categories': categories, 'hot_deals': hot_deals,  'must_haves': must_haves,'come_in_minutes': come_in_minutes,"new_arrivals": new_arrivals, 'page_obj': page_obj,'pharmacy_services': pharmacy_services})

def home(request):
    categories = Category.objects.all()
    pharmacy_services = PharmacyService.objects.filter(is_available=True)
    paginator = Paginator(categories, 21)  # 21 categories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    hot_deals = Product.objects.filter(is_hot_deal=True, is_available=True).order_by('-created_at')[:8]
    must_haves = Product.objects.filter(is_must_haves=True, is_available=True).order_by('-created_at')[:8]
    come_in_minutes = Product.objects.filter(come_in_minutes=True, is_available=True).order_by('-created_at')[:8]
    new_arrivals = Product.objects.filter(
        is_new_arrival=True,
        is_available=True
    ).order_by('-created_at')[:8]

    return render(request, 'index.html', {
        'categories': categories,
        'hot_deals': hot_deals,
        'must_haves': must_haves,
        'come_in_minutes': come_in_minutes,
        'new_arrivals': new_arrivals,
        'page_obj': page_obj,
        'pharmacy_services': pharmacy_services
    })

def medicine(request):
    categories = Category.objects.all()
    return render(request,'medicines.html',{'categories': categories})

def labtest(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    return render(request,'labtest.html', {'services': services,'categories': categories})

def service_booking(request, service_id):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    service = get_object_or_404(PharmacyService, id=service_id)

    if not service.is_available:
        return render(request, 'service_unavailable.html', {'service': service})

    booked_slots_qs = ServiceBooking.objects.filter(service=service).values_list('appointment_time', flat=True)
    booked_slots = [slot.strftime('%Y-%m-%dT%H:%M') for slot in booked_slots_qs]

    doctors = Doctor.objects.filter(is_available=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        test_type = request.POST.get('test_type', '')

        doctor_id = request.POST.get('doctor')
        doctor = get_object_or_404(Doctor, id=doctor_id) if doctor_id else None

        appointment_time_str = request.POST.get('appointment_time', '')
        appointment_time = datetime.strptime(appointment_time_str, '%Y-%m-%dT%H:%M') if appointment_time_str else datetime.now() + timedelta(days=1)

        price = service.price

        booking = ServiceBooking.objects.create(
            service=service,
            doctor=doctor,
            name=name,
            email=email,
            phone=phone,
            test_type=test_type,
            appointment_time=appointment_time,
            hospital_address="Main Hospital",
            price=price,
            payment_status='paid'
        )

        send_mail(
            subject=f'Booking Confirmation for {service.name}',
            message=f"""
Hi {booking.name},

Your booking for {booking.service.name} ({booking.test_type}) is confirmed.

Appointment Details:
Doctor: Mr./Mrs. {booking.doctor.name if booking.doctor else "Not Assigned"}
Specialty: {booking.doctor.specialty if booking.doctor else "-"}
Date & Time: {booking.appointment_time.strftime('%Y-%m-%d %H:%M')}
Address: {booking.hospital_address}

Payment Status: {booking.payment_status}
Amount Paid: ₹{booking.price}

Thank you for choosing our pharmacy!
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            fail_silently=False,
        )

        send_mail(
            subject=f'Payment Received for {service.name}',
            message=f"""
Hi {booking.name},

We have received your payment of ₹{booking.price} for {booking.service.name} ({booking.test_type}).

Your appointment is scheduled with Mr./Mrs. {booking.doctor.name if booking.doctor else "Not Assigned"} at {booking.appointment_time.strftime('%Y-%m-%d %H:%M')}.

Thank you!
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            fail_silently=False,
        )

        return redirect('booking_success', booking_id=booking.id)

    context = {
        'service': service,
        'doctors': doctors,
        'booked_slots': booked_slots,
        'categories': categories,
        'services': services,
    }
    return render(request, 'servicebooking.html', context)

def booking_success(request, booking_id):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    booking = get_object_or_404(ServiceBooking, id=booking_id)
    return render(request, 'bookingsucess.html', {'booking': booking,'categories': categories,'services': services,})

def consultdoc(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    doctor=Doctor.objects.all()
    return render(request,'consultdoc.html', {"MEDIA_URL": settings.MEDIA_URL,"doctor":doctor,'categories': categories,'services': services,})

def cancercare(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    cancer_meds = Product.objects.filter(categories__name__iexact='Cancer Care')    
    return render(request, "cancercare.html", {'cancer_meds': cancer_meds,'categories': categories,'services': services,})

def ayurveda(request):
    ayurvedic_meds = Product.objects.filter(categories__name__iexact='Ayurveda')
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    return render(request, "ayurveda.html", {'ayurvedic_meds': ayurvedic_meds,'categories': categories,'services': services,})

def signup_view(request):
    # categories = Category.objects.all()
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password1")
        confirm_password = request.POST.get("password2")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        birth_date = request.POST.get("birth_date")
        street_address = request.POST.get("street_address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zip_code = request.POST.get("zip_code")
        gender = request.POST.get("gender")
        contact_no = request.POST.get("contact_no")
        emergency_contact = request.POST.get("emergency_contact")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("signup")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("signup")

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date if birth_date else None,
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code,
            gender=gender,
            contact_no=contact_no,
            emergency_contact=emergency_contact,
        )
        messages.success(request, "You have successfully signed up to Meditrust!")
        return redirect('login')

    return render(request, "signuppage.html")

def login_view(request):
    # categories = Category.objects.all()
    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user_obj = CustomUser.objects.get(email=username_or_email)
            username = user_obj.username
        except CustomUser.DoesNotExist:
            username = username_or_email

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! You have successfully logged in.")
        else:
            messages.error(request, "Invalid username/email or password!")

    return render(request, "loginpage.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out!")
    return redirect('home')

@login_required(login_url='login')
def profile(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    user = request.user 
    orders = Order.objects.filter(user=user).order_by('-created_at')

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.birth_date = request.POST.get("birth_date")
        user.street_address = request.POST.get("street_address")
        user.city = request.POST.get("city")
        user.state = request.POST.get("state")
        user.zip_code = request.POST.get("zip_code")
        user.gender = request.POST.get("gender")
        user.contact_no = request.POST.get("contact_no")
        user.emergency_contact = request.POST.get("emergency_contact")
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if password1:
            if password1 == password2:
                user.set_password(password1)
            else:
                messages.error(request, "Passwords do not match!")
                return redirect("profile")

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, 'profilepage.html', {"user": user,'orders': orders,'categories': categories,'services': services,})

def partnership(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    products = Product.objects.all()
    wishlist_products = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    return render(request,'partnership.html', {'products': products,'wishlist_products': wishlist_products,'categories': categories,'services': services})

@login_required(login_url='login')
def toggle_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            wishlist_item.delete()
            return JsonResponse({'added': False})
        return JsonResponse({'added': True})

@login_required(login_url='login')
def wishlist(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    wishlist_products = Product.objects.filter(wishlist__user=request.user)
    return render(request, 'wishlist.html', {'wishlist_products': wishlist_products,'categories': categories,'services': services})

def careplan(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    products = Product.objects.all()
    wishlist_products = Product.objects.filter(wishlist__user=request.user).values_list('id', flat=True) if request.user.is_authenticated else []
    return render(request, 'careplan.html', {'products': products, 'wishlist_products': wishlist_products,'categories': categories,'services': services})

@login_required(login_url='login')
def delete_wishlist_item(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")

        try:
            product = Product.objects.get(id=product_id)
            Wishlist.objects.filter(user=request.user, product=product).delete()
            return JsonResponse({"deleted": True})
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required(login_url='login')
def cart(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.total_price for item in cart_items)
    discount_percent = 10
    discount = (subtotal * discount_percent) / 100
    delivery_fee = 50
    total = subtotal - discount + delivery_fee

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_percent': discount_percent,
        'discount': discount,
        'delivery_fee': delivery_fee,
        'total': total,
        'categories': categories,
        'services': services
    }
    return render(request,'cartpage.html',context)

from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='login')
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        print("Product ID received:", product_id)
        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'No product ID provided'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            print(f"Updated quantity: {cart_item.quantity}")
            return JsonResponse({'status': 'quantity_updated', 'quantity': cart_item.quantity})

        print("Added new product to cart")
        return JsonResponse({'status': 'added', 'quantity': cart_item.quantity})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def update_cart_quantity(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    action = request.POST.get('action')
    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
    item.save()
    return redirect('cart')

def remove_from_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')

def product_detail(request, id):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    product = get_object_or_404(Product, id=id)
    quantity_options = product.quantity_options.all()
    related_products = Product.objects.filter(
        Q(categories__in=product.categories.all()) |
        Q(subcategories__in=product.subcategories.all())
    ).exclude(id=product.id).distinct()[:4]
    products = Product.objects.all()

    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    else:
        wishlist_products = []

    context = {
        'product': product,
        'related_products': related_products,
        'products': products,
        'wishlist_products': wishlist_products,
        'categories': categories,
        'services': services,
        "quantity_options": quantity_options,
    }

    return render(request, 'product_detail.html', context)


@login_required(login_url='login')
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect('cart_page')

    subtotal = sum(item.total_price for item in cart_items)
    discount = sum(
        (item.product.mrp - item.product.selling_price) * item.quantity
        for item in cart_items if item.product.mrp > item.product.selling_price
    )
    total = subtotal  
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": "1",
    })

    context = {
        'user': user,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order['id'],
    }
    return render(request, 'checkout.html', context)

@login_required(login_url='login')
def payment_success(request):
    """Called after successful payment — create order, clear cart & show success message"""
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect('cart_page')

    total_amount = sum(item.total_price for item in cart_items)
    order = Order.objects.create(
        user=user,
        total_amount=total_amount,
        status='Paid'
    )
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.selling_price
        )

    cart_items.delete()
    return render(request, 'payment_success.html', {'order': order})

@login_required(login_url='login')
def ordered_items_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'ordered_items.html', {'orders': orders})

def product_listing(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    return render(request,'product_listing.html',{'categories': categories,'services': services})

def product_list(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    filter_type = request.GET.get('filter')

    products = Product.objects.filter(is_available=True)

    if category_id:
        products = products.filter(categories__id=category_id)

    if filter_type == 'hot_deals':
        products = products.filter(is_hot_deal=True)
    elif filter_type == 'must_haves':
        products = products.filter(is_must_haves=True)
    elif filter_type == 'come_in_minutes':
        products = products.filter(come_in_minutes=True)
    elif filter_type == 'new_arrivals':
        products = products.filter(is_new_arrival=True)

    if search_query:
        products = products.filter(name__icontains=search_query)

    categories = Category.objects.all()
    services = PharmacyService.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'search_query': search_query or '',
        'filter_type': filter_type or '',
        'services': services
    }
    return render(request, 'product_listing.html', context)


def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()

    if query:
        products = products.filter(
            name__icontains=query
        ) | products.filter(description__icontains=query)

    context = {
        'query': query,
        'products': products
    }
    return render(request, 'product_listing.html', context)

def book_service_payment(request, service_id):
    service = get_object_or_404(PharmacyService, id=service_id)
    doctors = Doctor.objects.filter(is_available=True)

    # debug print
    print("💚 book_service_payment view called for service:", service_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        "amount": int(service.price * 100),
        "currency": "INR",
        "payment_capture": "1",
    })

    context = {
        "service": service,
        "doctors": doctors,
        "razorpay_key": settings.RAZORPAY_KEY_ID,       # exactly this name
        "razorpay_order_id": razorpay_order["id"],      # exactly this name
        "total": service.price,                         # template will use total
    }
    return render(request, "servicebooking.html", context)

@login_required(login_url='login')
def service_payment_success(request):
    if request.method == "POST":
        # Payment details from Razorpay
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        service_id = request.POST.get('service_id')
        doctor_id = request.POST.get('doctor') or None
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        test_type = request.POST.get('test_type', '')
        appointment_time_str = request.POST.get('appointment_time', '')
        appointment_time = None

        if appointment_time_str:
            try:
                appointment_time = datetime.strptime(appointment_time_str, '%Y-%m-%dT%H:%M')
            except Exception:
                appointment_time = None

        price = request.POST.get('price') or 0

        service = get_object_or_404(PharmacyService, id=service_id)
        doctor = Doctor.objects.get(id=doctor_id) if doctor_id else None

        # Create a new booking record
        booking = ServiceBooking.objects.create(
            service=service,
            doctor=doctor,
            name=name,
            email=email,
            phone=phone,
            test_type=test_type,
            appointment_time=appointment_time,
            price=price,
            payment_status='paid',
            hospital_address="Sunrise Multispeciality Hospital, 42 MG Road, Sector 14, Gurugram, Haryana 122001"
        )

        messages.success(request, "Your appointment has been booked successfully!")
        return redirect('booking_success', booking_id=booking.id)

    return redirect('home')

def contact(request):
    categories = Category.objects.all()
    services = PharmacyService.objects.all()
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        ContactQuery.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        messages.success(request, "Your query has been submitted! Our team will contact you shortly through mail.")
        return redirect('contact')
    
    return render(request,'contactpage.html',{'categories': categories,'services': services})

def subscribe_view(request):
    if request.method == "POST":
        email = request.POST.get('email')

        # Check if already subscribed
        if Subscribe.objects.filter(email=email).exists():
            messages.info(request, "You're already subscribed to MediTrust updates!")
        else:
            Subscribe.objects.create(email=email)
            messages.success(request, "Thank you for subscribing to MediTrust! You'll now receive the latest updates.")
        
        return redirect('contact')  # redirect back to your contact page

    return redirect('contact')

def privacy(request):
    return render(request,'privacypage.html')

def terms(request):
    return render(request,'termspage.html')

def returnpolicy(request):
    return render(request,'returnpolicy.html')

def article(request):
    categories = ArticleCategory.objects.all()
    # Show all articles by default (when page loads)
    articles = Article.objects.all().order_by('-created_at')

    # Separate for layout (BIG + SMALL)
    big_article = articles.filter(article_type='BIG').first()
    small_articles = articles.filter(article_type='SMALL')[:2]

    context = {
        "categories": categories,
        "big_article": big_article,
        "small_articles": small_articles,
    }
    return render(request, 'articlespage.html', context)


def filter_articles(request, slug):
    if slug == "all":
        articles = Article.objects.all().order_by('-created_at')
    else:
        category = get_object_or_404(ArticleCategory, slug=slug)
        articles = Article.objects.filter(category=category).order_by('-created_at')

    big_article = articles.filter(article_type='BIG').first()
    small_articles = articles.filter(article_type='SMALL')[:2]

    data = {
        "big_article": None,
        "small_articles": [],
    }

    if big_article:
        data["big_article"] = {
            "title": big_article.title,
            "image": big_article.image.url if big_article.image else "",
            "short_description": big_article.short_description,
            "author": big_article.author,
            "created_at": big_article.created_at.strftime('%d %B %Y'),
        }

    for article in small_articles:
        data["small_articles"].append({
            "title": article.title,
            "image": article.image.url if article.image else "",
            "short_description": article.short_description,
            "author": article.author,
            "created_at": article.created_at.strftime('%d %B %Y'),
        })

    return JsonResponse(data)

import requests
from django.http import JsonResponse
from django.conf import settings

def auth_callback(request):
    shop = request.GET.get("shop")
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "No authorization code returned."})

    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": settings.SHOPIFY_API_KEY,
        "client_secret": settings.SHOPIFY_API_SECRET,
        "code": code,
    }

    response = requests.post(token_url, json=payload)
    data = response.json()

    print("ACCESS TOKEN:", data) 

    return JsonResponse(data)
