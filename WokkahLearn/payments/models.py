# payments/models.py

from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()

class SubscriptionPlan(models.Model):
    """Subscription plans available on the platform"""
    
    PLAN_TYPES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
        ('custom', 'Custom'),
    ]
    
    BILLING_INTERVALS = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('deprecated', 'Deprecated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_interval = models.CharField(max_length=20, choices=BILLING_INTERVALS)
    setup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    trial_period_days = models.IntegerField(default=0)
    
    # Features and Limits
    features = models.JSONField(default=dict)  # Feature flags and limits
    course_access_limit = models.IntegerField(null=True, blank=True)  # null = unlimited
    ai_interactions_limit = models.IntegerField(null=True, blank=True)
    collaboration_sessions_limit = models.IntegerField(null=True, blank=True)
    storage_limit_gb = models.IntegerField(null=True, blank=True)
    
    # AI Features Access
    ai_tutor_access = models.BooleanField(default=False)
    ai_mock_interviews = models.BooleanField(default=False)
    ai_code_review = models.BooleanField(default=False)
    ai_personalization = models.BooleanField(default=False)
    
    # Collaboration Features
    collaboration_rooms = models.BooleanField(default=False)
    peer_programming = models.BooleanField(default=False)
    mentorship_access = models.BooleanField(default=False)
    study_groups = models.BooleanField(default=False)
    
    # Advanced Features
    vr_ar_access = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    certification_access = models.BooleanField(default=False)
    white_label_access = models.BooleanField(default=False)
    
    # Payment Processing
    stripe_price_id = models.CharField(max_length=100, blank=True)
    stripe_product_id = models.CharField(max_length=100, blank=True)
    
    # Marketing
    description = models.TextField()
    is_featured = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['display_order', 'price']
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_interval}"


class UserSubscription(models.Model):
    """User subscription records"""
    
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('paused', 'Paused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    
    # Subscription Periods
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    trial_end_date = models.DateTimeField(null=True, blank=True)
    
    # Payment Information
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Billing
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    next_billing_date = models.DateTimeField(null=True, blank=True)
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    
    # Usage Tracking
    current_usage = models.JSONField(default=dict)  # Track usage against limits
    
    # Discounts and Promotions
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    promo_code_used = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        return self.status in ['trial', 'active']
    
    def has_feature(self, feature_name):
        """Check if subscription includes a specific feature"""
        return self.plan.features.get(feature_name, False)


class PaymentTransaction(models.Model):
    """Individual payment transactions"""
    
    TRANSACTION_TYPES = [
        ('subscription', 'Subscription Payment'),
        ('course_purchase', 'Course Purchase'),
        ('refund', 'Refund'),
        ('discount', 'Discount'),
        ('credit', 'Credit'),
        ('fee', 'Fee'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('stripe_card', 'Stripe Card'),
        ('stripe_bank', 'Stripe Bank Transfer'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('crypto', 'Cryptocurrency'),
        ('invoice', 'Invoice'),
        ('credit', 'Credit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Amount Information
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Payment Details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_processor = models.CharField(max_length=50, default='stripe')
    
    # External References
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True)
    external_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Related Objects
    subscription = models.ForeignKey(
        UserSubscription, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='transactions'
    )
    course_id = models.UUIDField(null=True, blank=True)
    
    # Transaction Details
    description = models.CharField(max_length=200)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Refund Information
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Failure Information
    failure_code = models.CharField(max_length=50, blank=True)
    failure_message = models.TextField(blank=True)
    
    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_transactions'
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_transaction_type_display()} - ${self.amount}"


class PromoCode(models.Model):
    """Promotional codes for discounts"""
    
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
        ('free_trial', 'Free Trial Extension'),
        ('feature_unlock', 'Feature Unlock'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
        ('depleted', 'Depleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Discount Configuration
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Usage Limits
    max_uses = models.IntegerField(null=True, blank=True)  # null = unlimited
    max_uses_per_user = models.IntegerField(default=1)
    current_uses = models.IntegerField(default=0)
    
    # Validity Period
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Targeting
    applicable_plans = models.ManyToManyField(SubscriptionPlan, blank=True)
    minimum_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    user_restrictions = models.JSONField(default=dict, blank=True)  # e.g., new users only
    
    # Features
    free_trial_days = models.IntegerField(default=0)
    unlocked_features = models.JSONField(default=list, blank=True)
    
    # Stripe Integration
    stripe_coupon_id = models.CharField(max_length=100, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_promo_codes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'promo_codes'
        verbose_name = 'Promo Code'
        verbose_name_plural = 'Promo Codes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_valid(self):
        """Check if promo code is currently valid"""
        from django.utils import timezone
        now = timezone.now()
        
        if self.status != 'active':
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        
        return True


class PromoCodeUsage(models.Model):
    """Track promo code usage by users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_code_usages')
    transaction = models.ForeignKey(
        PaymentTransaction, 
        on_delete=models.CASCADE, 
        related_name='promo_usage',
        null=True,
        blank=True
    )
    
    # Usage Details
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    original_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'promo_code_usage'
        verbose_name = 'Promo Code Usage'
        verbose_name_plural = 'Promo Code Usage'
        unique_together = ['promo_code', 'user', 'transaction']
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.user.full_name} used {self.promo_code.code}"


class PaymentMethod(models.Model):
    """Stored payment methods for users"""
    
    METHOD_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('bank_account', 'Bank Account'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Payment Processor Data
    stripe_payment_method_id = models.CharField(max_length=100, blank=True)
    
    # Display Information (masked for security)
    display_name = models.CharField(max_length=100)  # e.g., "**** 4242"
    brand = models.CharField(max_length=50, blank=True)  # e.g., "Visa"
    last_four = models.CharField(max_length=4, blank=True)
    exp_month = models.IntegerField(null=True, blank=True)
    exp_year = models.IntegerField(null=True, blank=True)
    
    # Billing Address
    billing_address = models.JSONField(default=dict, blank=True)
    
    # Usage
    is_default = models.BooleanField(default=False)
    last_used = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['-is_default', '-last_used']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.display_name}"


class Invoice(models.Model):
    """Invoices for payments"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('void', 'Void'),
        ('uncollectible', 'Uncollectible'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(
        UserSubscription, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='invoices'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Invoice Information
    invoice_number = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Currency and Tax
    currency = models.CharField(max_length=3, default='USD')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    
    # Dates
    issue_date = models.DateTimeField()
    due_date = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Line Items
    line_items = models.JSONField(default=list)
    
    # Stripe Integration
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    
    # File Storage
    pdf_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.full_name}"


class PaymentAttempt(models.Model):
    """Track payment attempts for failed payments"""
    
    ATTEMPT_TYPES = [
        ('automatic', 'Automatic Retry'),
        ('manual', 'Manual Retry'),
        ('dunning', 'Dunning Process'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='payment_attempts')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payment_attempts')
    attempt_type = models.CharField(max_length=20, choices=ATTEMPT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Attempt Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Results
    success = models.BooleanField(default=False)
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    
    # Retry Logic
    retry_number = models.IntegerField(default=1)
    next_retry_date = models.DateTimeField(null=True, blank=True)
    
    # External References
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    
    attempted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_attempts'
        verbose_name = 'Payment Attempt'
        verbose_name_plural = 'Payment Attempts'
        ordering = ['-attempted_at']
    
    def __str__(self):
        return f"Payment Attempt {self.retry_number} for {self.subscription}"