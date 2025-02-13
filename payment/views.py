from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from decimal import Decimal

import stripe
from orders.models import Order
from django.urls import reverse

# Set Stripe API keys
stripe.api_key = settings.STRIPE_API_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    # Retrieve order ID from session
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('cart')  # Redirect if no order ID is found

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        # Prepare session data for Stripe
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'payment_method_types': ['card'],
            'line_items': []  # Start with an empty line items list
        }

        # Add items to line_items for Stripe checkout session
        for item in order.items.all():
            if item.price and item.quantity:  # Ensure the item has a price and quantity
                session_data['line_items'].append({
                    'price_data': {
                        'unit_amount': int(item.price * Decimal('100')),  # Convert price to cents
                        'currency': 'usd',  # Make sure the currency is valid
                        'product_data': {
                            'name': item.product.name,
                        },
                    },
                    'quantity': int(item.quantity),
                })

        # If no line items were added, redirect to cart page
        if not session_data['line_items']:
            return redirect('cart')  # Or display an error message

        # Create Stripe session
        try:
            session = stripe.checkout.Session.create(**session_data)
            return redirect(session.url, code=303)
        except stripe.error.StripeError as e:
            # Log error and return error page
            print(f"Stripe error: {e}")
            return render(request, 'payment/error.html', {'error': str(e)})

    return render(request, 'payment/process.html', locals())

def payment_success(request):
    return render(request, 'payment/completed.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')
