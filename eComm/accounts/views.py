from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import LoginForm, RegisterForm
from accounts.forms import AddressForm
from accounts.models import BillingProfile
from orders.models import Order
from carts.models import Cart
# Create your views here.


def login_page(request):
    form = LoginForm(request.POST or None)
    context = {
        'title': "Please Login!", 
        'form': form,
    }
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        print("User Logged in : ", request.user.is_authenticated)
        # Redirect to a success page.
        messages.success(request, "Login Successful.")
        return redirect('/')
    else:
        # Return an 'invalid login' error message.
        print("Error...")
    
    return render(request, 'accounts/login.html', context=context)

def register_page(request):
    form = RegisterForm(request.POST or None)
    context = {
        'title': "Register Yourself", 
        'form': form,
    }
    username = request.POST.get('username')
    email    = request.POST.get('email')
    password = request.POST.get('password')
    if form.is_valid():
        user = User.objects.create_user(username=username, email=email, password=password)
        print("User created : ", user)
        messages.success(request, f"User: - '{user}' successfully Added.")
        print(form.cleaned_data)
    return render(request, 'accounts/register.html', context=context)


def logout_page(request):
    if request.user.is_authenticated:
        print("User logged out : ", request.user)
        messages.success(request, "Logged Out ")
        logout(request)
        return redirect("/login")
    else:
        messages.error(request, "Logging out failed...")


def address_create_view(request):
    form = AddressForm(request.POST or None)

    if form.is_valid():
        print(request.POST)
        instance = form.save(commit=False)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request=request)
        cart_obj = Cart.objects.new_or_get(request=request)

        if billing_profile is not None:
            order_obj, order_obj_created = Order.objects.new_or_get(cart_obj=cart_obj, billing_profile=billing_profile)
            payment_method = request.POST.get("payment_method", None)
            if payment_method:
                order_obj.payment_method = payment_method
                order_obj.save()
            instance.billing_profile = billing_profile
            instance.save()
            request.session['billing_address_id'] = instance.id
        else:
            messages.error(request, "Might have some problem....!")
            return redirect("cart:checkout")

    return redirect("cart:checkout")
