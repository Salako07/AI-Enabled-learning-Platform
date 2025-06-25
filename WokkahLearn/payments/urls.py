from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'plans', views.SubscriptionPlanViewSet)
router.register(r'subscriptions', views.UserSubscriptionViewSet)
router.register(r'transactions', views.PaymentTransactionViewSet)
router.register(r'payment-methods', views.PaymentMethodViewSet)
router.register(r'invoices', views.InvoiceViewSet)

urlpatterns = [
    # Subscription Management
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('cancel-subscription/', views.CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('update-subscription/', views.UpdateSubscriptionView.as_view(), name='update_subscription'),
    
    # Payment Processing
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('confirm-payment/', views.ConfirmPaymentView.as_view(), name='confirm_payment'),
    
    # Payment Methods
    path('payment-methods/add/', views.AddPaymentMethodView.as_view(), name='add_payment_method'),
    path('payment-methods/<uuid:method_id>/set-default/', views.SetDefaultPaymentMethodView.as_view(), name='set_default_payment_method'),
    
    # Promo Codes
    path('promo-codes/validate/', views.ValidatePromoCodeView.as_view(), name='validate_promo_code'),
    path('promo-codes/apply/', views.ApplyPromoCodeView.as_view(), name='apply_promo_code'),
    
    # Billing
    path('billing-portal/', views.BillingPortalView.as_view(), name='billing_portal'),
    path('invoices/<uuid:invoice_id>/download/', views.DownloadInvoiceView.as_view(), name='download_invoice'),
    
    # Webhooks
    path('webhooks/stripe/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]
