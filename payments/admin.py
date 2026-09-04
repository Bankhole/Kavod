from django.contrib import admin

from .models import Invoice, PaymentCategory, Transaction


@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'student', 'category', 'amount', 'status', 'created_at')
    list_filter = ('status', 'academic_session', 'term', 'category')
    search_fields = ('reference', 'student__username', 'student__email')
    readonly_fields = ('reference', 'gateway_response')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'student', 'status', 'total_amount', 'due_date', 'remaining_days')
    list_filter = ('status', 'academic_session', 'term')
    search_fields = ('invoice_number', 'student__username', 'student__email', 'billing_phone', 'billing_email')
    readonly_fields = ('invoice_number', 'issue_date', 'total_amount')
    fieldsets = (
        ('Invoice Details', {
            'fields': ('invoice_number', 'student', 'transaction', 'academic_session', 'term', 'issue_date', 'due_date', 'status')
        }),
        ('Student Contact Details', {
            'fields': ('billing_name', 'billing_email', 'billing_phone', 'billing_address')
        }),
        ('Charges', {
            'fields': ('itemized_charges', 'tuition_fee', 'late_registration_fee', 'other_charges', 'total_amount', 'notes')
        }),
    )

    def remaining_days(self, obj):
        return obj.remaining_days
    remaining_days.short_description = 'Days left'
