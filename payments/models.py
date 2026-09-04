import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class PaymentCategory(models.Model):
    """School payment categories such as tuition, excursion, uniform, and exams."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Default/standard amount")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Payment Categories"

    def __str__(self):
        return f"{self.name} - ₦{self.amount}"


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESSFUL = 'SUCCESSFUL', 'Successful'
        FAILED = 'FAILED', 'Failed'

    reference = models.CharField(max_length=100, unique=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(PaymentCategory, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    academic_session = models.CharField(max_length=20, help_text="e.g. 2025/2026")
    term = models.CharField(max_length=20, choices=[('1st', 'First Term'), ('2nd', 'Second Term'), ('3rd', 'Third Term')])
    gateway_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.category.name} ({self.status})"


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SENT = 'SENT', 'Sent'
        PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'

    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    academic_session = models.CharField(max_length=20, help_text="e.g. 2025/2026")
    term = models.CharField(max_length=20, choices=[('1st', 'First Term'), ('2nd', 'Second Term'), ('3rd', 'Third Term')])
    issue_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    billing_name = models.CharField(max_length=200, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_phone = models.CharField(max_length=20, blank=True)
    billing_address = models.TextField(blank=True)
    itemized_charges = models.JSONField(default=list, blank=True, help_text='Example: [{"title": "Tuition Fee", "amount": "350000.00"}]')
    tuition_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    late_registration_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.invoice_number} - {self.student.get_full_name() or self.student.username}"

    @property
    def student_name(self):
        return self.student.get_full_name() or self.student.username

    @property
    def student_phone(self):
        profile = getattr(self.student, 'profile', None)
        if self.billing_phone:
            return self.billing_phone
        if profile and profile.phone_number:
            return profile.phone_number
        return ''

    @property
    def student_address(self):
        profile = getattr(self.student, 'profile', None)
        if self.billing_address:
            return self.billing_address
        if profile:
            parts = [profile.address, profile.city, profile.state, profile.country]
            return ', '.join(filter(None, parts))
        return ''

    @property
    def payer_name(self):
        return self.billing_name or self.student_name

    @property
    def payer_email(self):
        return self.billing_email or self.student.email or ''

    @property
    def payer_phone(self):
        return self.billing_phone or self.student_phone

    @property
    def payer_address(self):
        return self.billing_address or self.student_address

    @property
    def contact_details(self):
        return {
            'name': self.payer_name,
            'email': self.payer_email,
            'phone': self.payer_phone,
            'address': self.payer_address,
        }

    @property
    def subtotal(self):
        total = Decimal('0.00')
        for item in self.itemized_charges:
            raw = item.get('amount', '0')
            try:
                total += Decimal(str(raw))
            except Exception:
                continue
        try:
            total += Decimal(str(self.tuition_fee))
        except Exception:
            pass
        return total

    def calculate_total(self):
        subtotal = self.subtotal
        try:
            total = subtotal + Decimal(str(self.late_registration_fee)) + Decimal(str(self.other_charges))
        except Exception:
            total = subtotal
        return total

    @property
    def remaining_days(self):
        today = timezone.localdate()
        delta = self.due_date - today
        return max(delta.days, 0)

    @property
    def countdown_display(self):
        today = timezone.localtime(timezone.now())
        deadline = timezone.datetime.combine(self.due_date, timezone.datetime.min.time(), tzinfo=today.tzinfo)
        delta = deadline - today
        total_seconds = max(int(delta.total_seconds()), 0)

        if total_seconds <= 0:
            return 'Due now'

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days:
            parts.append(f'{days} day{"s" if days != 1 else ""}')
        if hours:
            parts.append(f'{hours} hour{"s" if hours != 1 else ""}')
        if minutes and not days:
            parts.append(f'{minutes} minute{"s" if minutes != 1 else ""}')
        if not parts and seconds:
            parts.append(f'{seconds} second{"s" if seconds != 1 else ""}')

        return ' '.join(parts) + ' left' if parts else 'Due today'

    @property
    def is_overdue(self):
        return self.due_date < timezone.localdate() and self.status != self.Status.PAID

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:10].upper()}"
        if not self.billing_name:
            self.billing_name = self.student_name
        if not self.billing_email:
            self.billing_email = self.student.email or ''
        if not self.billing_phone:
            profile = getattr(self.student, 'profile', None)
            self.billing_phone = profile.phone_number if profile and profile.phone_number else ''
        if not self.billing_address:
            profile = getattr(self.student, 'profile', None)
            if profile:
                address_parts = [profile.address, profile.city, profile.state, profile.country]
                self.billing_address = ', '.join(filter(None, address_parts))
            else:
                self.billing_address = ''
        self.total_amount = self.calculate_total()
        if self.due_date and self.due_date < timezone.localdate() and self.status != self.Status.PAID:
            self.status = self.Status.OVERDUE
        super().save(*args, **kwargs)
