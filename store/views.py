from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import HttpResponse

# https://www.youtube.com/watch?v=86KSu7aC0Ck&t=200s  where to get this info about paypal django
# Import some paypal stuff
# reverse sends us back, make payment gets reversed back to some page on our website from paypal
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
# below allows us to create unique user id for duplicate orders.
import uuid 

# Create your views here.

# @login_required
def store(request):
    user = request.user
    if request.user.is_authenticated:
        if not hasattr(user, 'customer'):
            Customer.objects.create(user=user, name=user.username, email=user.email)
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

# @login_required
def cart(request):
    user = request.user
    if request.user.is_authenticated:
        if not hasattr(user, 'customer'):
            Customer.objects.create(user=user, name=user.username, email=user.email)
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

    # Get the current order
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Validate the total amount
    total = float(data['form']['total'])
    if total != order.get_cart_total:
        return JsonResponse({'error': 'Invalid total amount'}, status=400)

    # Update the order with transaction details
    order.transaction_id = transaction_id
    order.complete = False  # Mark as incomplete until payment is confirmed
    order.save()

    # Save shipping details if required
    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    # PayPal payment details
    host = request.get_host()
    paypal_dict = {
        'cmd': '_xclick',  # Command for a single item purchase
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total, 
        'item_name': f'Order {order.id}',
        'no_shipping': '2',  # No shipping required
        'invoice': str(uuid.uuid4()),  # Unique invoice ID
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,reverse('payment_success')),
        'cancel_return': 'http://{}{}'.format(host,reverse('payment_cancel')),
        'custom': str(request.user.id),  # Add custom field for user identification
    }

    # Generate PayPal form
    form = PayPalPaymentsForm(initial=paypal_dict)

    # Render the PayPal form in the response
    return JsonResponse({
        'message': 'Payment initiated',
        'paypal_form': form.render(),  # Render the PayPal form as HTML
    })

    #  paypal payment view

# @login_required
# def paypal_payment(request):
#     user = request.user
#     if not hasattr(user, 'customer'):
#         Customer.objects.create(user=user, name=user.username, email=user.email)

#     customer = request.user.customer
#     order, created = Order.objects.get_or_create(customer=customer, complete=False)

#     host = request.get_host()

#     # PayPal payment details
#     paypal_dict = {
#         'cmd': '_xclick',  # Command for a single item purchase
#         'business': settings.PAYPAL_RECEIVER_EMAIL,
#         'amount': f"{order.get_cart_total:.2f}",  # Ensure proper formatting
#         'item_name': f'Order {order.id}',
#         'no_shipping': '1',  # No shipping required
#         'invoice': str(order.id),  # Unique invoice ID
#         'currency_code': 'USD',
#         'notify_url': f"http://{host}{reverse('paypal-ipn')}",
#         'return_url': f"http://{host}{reverse('payment_success')}",
#         'cancel_return': f"http://{host}{reverse('payment_cancel')}",
#         'custom': str(request.user.id),  # Add custom field for user identification
#     }

#     # Generate PayPal form
#     form = PayPalPaymentsForm(initial=paypal_dict)
#     context = {'form': form, 'order': order}
#     return render(request, 'paypal_payment.html', context)


@login_required
def payment_success(request):
    return HttpResponse("Payment completed successfully!")

@login_required
def payment_cancel(request):
    return HttpResponse("Payment was canceled.")