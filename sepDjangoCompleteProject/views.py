from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Product

import requests
from django.http import HttpResponse
from requests.auth import HTTPBasicAuth
import json
from . credentials import *

def home(request):
    return render(request, 'index.html')


@login_required()
def add_products(request):
    if request.method == "POST":
        prod_name = request.POST.get('p-name')
        prod_quantity = request.POST.get('p-quantity')
        prod_price = request.POST.get('p-price')
        prod_desc = request.POST.get('p-description')
        product_data = Product(name=prod_name,
                               quantity=prod_quantity,
                               price=prod_price,
                               desc=prod_desc)
        product_data.save()
        messages.success(request, 'saved successfully')
        return redirect('add-prod-url')
    return render(request, 'add-products.html')


@login_required()
def view_products(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'view-product.html', context)


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User creation success')
            return redirect('register-url')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def delete(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    messages.success(request, 'Delete successfully')
    return redirect('view-prod-url')


def update_product(request, id):
    product = Product.objects.get(id=id)
    context = {'product': product}
    if request.method == "POST":
        updated_name = request.POST.get('p-name')
        updated_quantity = request.POST.get('p-quantity')
        updated_price = request.POST.get('p-price')
        updated_description = request.POST.get('p-description')

        product.name = updated_name
        product.quantity = updated_quantity
        product.price = updated_price
        product.desc = updated_description

        product.save()
        messages.success(request, 'updated successfully')
        return redirect('view-prod-url')
    return render(request, 'update-products.html', context)


def token(request):
    consumer_key = '77bgGpmlOxlgJu6oEXhEgUgnu0j2WYxA'
    consumer_secret = 'viM8ejHgtEmtPTHd'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]
    return render(request, 'token.html', {"token": validated_mpesa_access_token})


def pay(request, id):
    product = Product.objects.get(id=id)
    context = {'product': product}

    if request.method == "POST":
        phone = request.POST['phone-number']
        amount = product.price
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPassword.Business_short_code,
            "Password": LipanaMpesaPassword.decode_password,
            "Timestamp": LipanaMpesaPassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "PYMENT001",
            "TransactionDesc": "school fees"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return HttpResponse("success")

    return render(request, 'pay.html', context)
