from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from .models import OrderItem, Order
from .forms import OrderCreateForm
from .tasks import order_created

from django.contrib.admin.views.decorators import staff_member_required

import weasyprint
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import render_to_string


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})

    # Create the response with content type as PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order_id}.pdf'

    # Generate the PDF from HTML
    weasyprint.HTML(string=html).write_pdf(response)

    # If you need to use custom CSS (optional)
    stylesheets = [weasyprint.CSS(finders.find('css/pdf.css'))]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)

    return response

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order = order,
                    product = item['product'],
                    price = item['price'],
                    quantity = item['quantity'],
                )
            cart.clear()
            order_created.delay(order.id)
            # set the order in the session
            request.session['order_id'] = order.id
            # redirect for payment
            return redirect('payment:process')
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', context={'form': form, 'cart': cart})

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(
        request, 'orders/admin/order/detail.html', {'order': order}
    )