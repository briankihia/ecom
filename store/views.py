from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth.decorators import login_required
from .models import *

# https://www.youtube.com/watch?v=86KSu7aC0Ck&t=200s  where to get this info about paypal django
# Import some paypal stuff
# reverse sends us back, make payment gets reversed back to some page on our website from paypal
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
# below allows us to create unique user id for duplicate orders.
import uuid 

# Create your views here.

@login_required
def store(request):
    user = request.user
    if not hasattr(user, 'customer'):
        Customer.objects.create(user=user, name=user.username, email=user.email)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # here we are creating an object or query one
        # in our get_or_create ...the order we are looking for is,our customer here that we queried and we also want to get the order that has a completed status of false(open order or open cart)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}
        cartItems = order['get_cart_items']


    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems, 'user_name': user.username}
    return render(request, 'store.html', context)

@login_required
def cart(request):
    user = request.user
    if not hasattr(user, 'customer'):
        Customer.objects.create(user=user, name=user.username, email=user.email)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # here we are creating an object or query one
        # in our get_or_create ...the order we are looking for is,our customer here that we queried and we also want to get the order that has a completed status of false(open order or open cart)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False }
        cartItems = order['get_cart_items']

    context = {'items':items, 'order':order,'cartItems':cartItems, 'user_name': user.username}
    return render(request, 'cart.html', context)

@login_required
def checkout(request):
    user = request.user
    if not hasattr(user, 'customer'):
        Customer.objects.create(user=user, name=user.username, email=user.email)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # here we are creating an object or query one
        # in our get_or_create ...the order we are looking for is,our customer here that we queried and we also want to get the order that has a completed status of false(open order or open cart)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        # create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order':order, 'cartItems':cartItems, 'user_name': user.username}
    return render(request, 'checkout.html', context)

@login_required
def updateItem(request):
    user = request.user
    if not hasattr(user, 'customer'):
        Customer.objects.create(user=user, name=user.username, email=user.email)
    # we set the value of data to that response
    data = json.loads(request.body)
    # here we are getting the values of productId  and action
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:',productId)
    

    customer = request.user.customer
    product = Product.objects.get(id= productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)


    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity -1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()


    return JsonResponse("Item was added", safe=False)


# this means whenever data is sent to that view,dont worry about it just let that data go in
# the reason why this is okay is because we are not actually sending any credit card data to our form.All that is done by paypal so we are not really vulnerable to issues
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@login_required
def processOrder(request):
    user = request.user
    if not hasattr(user, 'customer'):
        Customer.objects.create(user=user, name=user.username, email=user.email)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            shippingAddress.objects.create(
                customer=customer,
                order=order,
                address= data['shipping']['address'],
                city= data['shipping']['city'],
                state= data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

    else:
        print("User is not logged in ..")

    return JsonResponse('Payment submitted!', safe=False)