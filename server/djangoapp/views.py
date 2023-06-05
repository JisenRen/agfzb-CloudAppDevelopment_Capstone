from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .restapis import *
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)
# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['password']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
    return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def signup_page(request):
    context = {}
    return render(request, 'djangoapp/registration.html', context)

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return redirect('djangoapp:signup')
    user_exists = User.objects.filter(username=request.POST['username']).exists()
    if not user_exists:
        user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'])
        login(request, user)
    else:
        password_match = User.objects.filter(username=request.POST['username'], password=request.POST['password']).exists()
        if password_match:
            user = User.objects.get(username=request.POST['username'])
            login(request, user)
    return redirect('djangoapp:index')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/c87e0f7b-1770-4c6a-976e-5e2defce6749/dealership-package/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        # Concat all dealer's short name
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == 'GET':
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/c87e0f7b-1770-4c6a-976e-5e2defce6749/dealership-package/review"
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context['reviews'] = reviews
        context['dealerId'] = dealer_id
        # return HttpResponse('\r\n'.join([(x.review+'\t'+x.sentiment) for x in reviews]))
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {"dealerId": dealer_id, "cars": CarMake.objects.all()}
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/c87e0f7b-1770-4c6a-976e-5e2defce6749/dealership-package/review"
    if request.method == 'GET':
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        body = {}
        body['review'] = request.POST['content']
        body['dealership'] = dealer_id
        body['id'] = 0
        body['name'] = request.POST['name']
        body['purchase'] = request.POST['purchasecheck']
        body['purchase_date'] = request.POST['purchasedate']
        car = request.POST['car']
        car_id = car.split('>')[0]
        post_request(url, {'review': body})
        return redirect('djangoapp:dealer_details', dealerId=dealer_id)

