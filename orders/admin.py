from django.contrib import admin
from django.utils.http import content_disposition_header

from .models import Order, OrderItem
from django.utils.safestring import mark_safe

from django.urls import reverse

import csv
import datetime
from django.http import HttpResponse

def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')
order_pdf.short_description = 'Invoice'

def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = (
        f'attachment; filename={opts.verbose_name}.csv'
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    writer.writerow(fields)
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV'

def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=(obj.id,))
    return mark_safe(f'<a href="{url}">view</a>')

def order_payment(obj):
 url = obj.get_stripe_url()
 if obj.stripe_id:
     html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
     return mark_safe(html)
 return ''
order_payment.short_description = 'Stripe payment'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'first_name', 'last_name',
        'email', 'address', order_payment,
        'city', 'postal_code', 'created',
        'updated', 'paid', order_detail,
        order_pdf,
    )
    list_filter = ('paid', 'created', 'updated')
    inlines = [OrderItemInline]
    actions = [export_to_csv]







