from django.urls import path
from . import views, webhooks
from django.conf import settings
from django.conf.urls.static import static

app_name = 'payment'
urlpatterns = [
    path('process/',views.payment_process,name='process' ),
    path('completed/',views.payment_success,name='completed' ),
    path('canceled/', views.payment_canceled, name='canceled' ),
    path('webhook/', webhooks.stripe_webhook, name='.stripe_webhook' ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)