from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.core.mail import send_mail


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data.get('productId')
    action = data.get('action')

    print('Action:', action)
    print('Product:', productId)

    product = Product.objects.get(id=productId)
    message = ''

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity += 1
            message = f"Added one '{product.name}' to your cart."
        elif action == 'remove':
            orderItem.quantity -= 1
            if orderItem.quantity <= 0:
                orderItem.delete()
                message = f"Removed '{product.name}' from your cart."
            else:
                message = f"Decreased quantity of '{product.name}' in your cart."

        if orderItem.pk:
            orderItem.save()

        if request.user.email:
            subject = f"Cart Updated: {action.capitalize()} '{product.name}'"
            body = (
                f"Hi {request.user.username},\n\n"
                f"You {action}ed '{product.name}' in your cart.\n\n"
                f"Regards,\nRehanMart"
            )
            send_mail(subject, body, None, [request.user.email])

    else:
        if action == 'add':
            message = f"Added one '{product.name}' to your cart."
        elif action == 'remove':
            message = f"Removed one '{product.name}' from your cart."

        subject = f"Guest User Cart Updated: {action.capitalize()} '{product.name}'"
        body = f"A guest user has {action}ed the item '{product.name}' in the cart."
        send_mail(subject, body, None, ['admin@example.com'])  

    return JsonResponse({'message': message}, safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=False).first()
        if not order:
            order = Order.objects.create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)
