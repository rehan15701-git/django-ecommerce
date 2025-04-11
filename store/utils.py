import json
from django.core.mail import send_mail
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        print('CART:', cart)

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = product.price * cart[i]['quantity']

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'id': product.id,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL
                },
                'quantity': cart[i]['quantity'],
                'digital': product.digital,
                'get_total': total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item['id'])
        OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )

    product_list = ", ".join([item['product']['name'] for item in items])
    admin_msg = f"Guest user '{name}' ({email}) placed an order for: {product_list}"
    guest_msg = f"Hi {name},\n\nThanks for placing an order with us. You ordered: {product_list}\n\nWe'll process it soon."

    try:
        send_mail(
            subject="New Guest Order",
            message=admin_msg,
            from_email='rehanmart@example.com',
            recipient_list=['kobe@kobe.com'],
            fail_silently=False,
        )

        send_mail(
            subject="Order Confirmation",
            message=guest_msg,
            from_email='rehanmart@example.com',
            recipient_list=[email],
            fail_silently=False,
        )

        print("Emails sent.")
    except Exception as e:
        print("Error sending email:", str(e))

    return customer, order
