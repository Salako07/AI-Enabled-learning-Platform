from rest_framework import serializers
from .models import (
    SubscriptionPlan, UserSubscription, PaymentTransaction,
    PaymentMethod, Invoice, PromoCode
)

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'price', 'billing_interval',
            'trial_period_days', 'features', 'course_access_limit',
            'ai_interactions_limit', 'ai_tutor_access', 'ai_mock_interviews',
            'collaboration_rooms', 'vr_ar_access', 'priority_support',
            'description', 'is_featured', 'is_popular'
        ]

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_features = serializers.JSONField(source='plan.features', read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'plan', 'plan_name', 'plan_features', 'status',
            'start_date', 'end_date', 'current_period_start',
            'current_period_end', 'cancel_at_period_end',
            'current_usage', 'discount_percentage'
        ]

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'transaction_type', 'status', 'amount', 'currency',
            'payment_method', 'description', 'processed_at', 'created_at'
        ]

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'method_type', 'display_name', 'brand', 'last_four',
            'exp_month', 'exp_year', 'is_default', 'last_used'
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'status', 'subtotal', 'tax_amount',
            'total_amount', 'amount_due', 'issue_date', 'due_date',
            'paid_at', 'pdf_url'
        ]

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = [
            'id', 'code', 'name', 'description', 'discount_type',
            'discount_value', 'valid_from', 'valid_until',
            'current_uses', 'max_uses'
        ]
        read_only_fields = ['current_uses']