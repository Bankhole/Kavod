from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from accounts.permissions import can_manage_school_operations
from .forms import BulkInvoiceForm
from .models import Invoice, PaymentCategory, Transaction
from .services import GatewayServiceFactory
from .utils import generate_invoice_pdf, generate_receipt_pdf


def _can_manage_invoices(user):
    return can_manage_school_operations(user)


@login_required
def payment_dashboard(request):
    """Displays payment options for school fees and other charges."""
    categories = PaymentCategory.objects.filter(is_active=True)
    recent_invoices = Invoice.objects.filter(student=request.user).order_by('-issue_date')[:5]
    can_manage_invoices = _can_manage_invoices(request.user)
    if can_manage_invoices:
        students = get_user_model().objects.filter(role='STUDENT').order_by('first_name', 'last_name', 'username')
        recent_all_invoices = Invoice.objects.select_related('student').order_by('-issue_date')[:8]
    else:
        students = []
        recent_all_invoices = []

    return render(
        request,
        'payments/dashboard.html',
        {
            'categories': categories,
            'recent_invoices': recent_invoices,
            'students': students,
            'recent_all_invoices': recent_all_invoices,
            'can_manage_invoices': can_manage_invoices,
        },
    )


@login_required
def initiate_payment(request, category_id):
    """Creates a pending transaction and redirects to a chosen gateway."""
    category = get_object_or_404(PaymentCategory, id=category_id)
    gateway_name = request.GET.get('gateway', 'paystack').lower()

    transaction = Transaction.objects.create(
        student=request.user,
        category=category,
        amount=category.amount,
        academic_session='2025/2026',
        term='1st',
        status=Transaction.Status.PENDING,
    )

    callback_url = request.build_absolute_uri(reverse('payments:verify_payment'))
    gateway_service = GatewayServiceFactory.get(gateway_name)
    response = gateway_service.initialize_transaction(
        email=request.user.email,
        amount_in_kobo=transaction.amount,
        reference=transaction.reference,
        callback_url=callback_url,
    )

    if response.get('status'):
        auth_url = response['data'].get('authorization_url') or response['data'].get('checkout_url')
        if auth_url:
            return redirect(auth_url)

    messages.error(request, 'Could not initiate payment. Please try again.')
    return redirect('payments:dashboard')


@login_required
def verify_payment(request):
    """Callback URL where the selected gateway redirects after payment completes."""
    reference = request.GET.get('reference')
    gateway_name = request.GET.get('gateway', 'paystack').lower()

    if not reference:
        messages.error(request, 'No reference key was provided.')
        return redirect('payments:dashboard')

    transaction = get_object_or_404(Transaction, reference=reference)
    gateway_service = GatewayServiceFactory.get(gateway_name)
    verification = gateway_service.verify_transaction(reference)

    if verification.get('status') and verification['data'].get('status') == 'success':
        transaction.status = Transaction.Status.SUCCESSFUL
        transaction.gateway_response = verification['data']
        transaction.save()
        Invoice.objects.filter(transaction=transaction).update(status=Invoice.Status.PAID)
        messages.success(request, f'Payment for {transaction.category.name} was successful.')
    else:
        transaction.status = Transaction.Status.FAILED
        transaction.gateway_response = verification
        transaction.save()
        messages.error(request, 'Payment failed or was cancelled.')

    return redirect('payments:history')


@login_required
def payment_history(request):
    """Shows past payment history for the logged-in user."""
    user_transactions = Transaction.objects.filter(student=request.user)

    status_filter = request.GET.get('status')
    if status_filter:
        user_transactions = user_transactions.filter(status=status_filter)

    return render(request, 'payments/history.html', {'transactions': user_transactions})


@login_required
@user_passes_test(_can_manage_invoices)
@transaction.atomic
def manual_invoice_entry(request, invoice_number=None):
    User = get_user_model()
    students = User.objects.filter(role='STUDENT').order_by('first_name', 'last_name', 'username')
    invoice = None

    if invoice_number:
        invoice = get_object_or_404(Invoice, invoice_number=invoice_number)

    initial = {
        'student_id': invoice.student_id if invoice else '',
        'academic_session': invoice.academic_session if invoice else '2026/2027',
        'term': invoice.term if invoice else '1st',
        'billing_name': invoice.billing_name if invoice else '',
        'billing_email': invoice.billing_email if invoice else '',
        'billing_phone': invoice.billing_phone if invoice else '',
        'billing_address': invoice.billing_address if invoice else '',
        'tuition_fee': invoice.tuition_fee if invoice else '0',
        'late_registration_fee': invoice.late_registration_fee if invoice else '0',
        'other_charges': invoice.other_charges if invoice else '0',
        'notes': invoice.notes if invoice else '',
    }

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if not student_id:
            messages.error(request, 'Please select a student before saving the invoice.')
            return render(request, 'payments/manual_invoice_entry.html', {'students': students, 'initial': initial, 'invoice': invoice})

        student = get_object_or_404(User, id=student_id)
        academic_session = request.POST.get('academic_session') or '2026/2027'
        term = request.POST.get('term') or '1st'
        billing_name = (request.POST.get('billing_name') or '').strip() or student.get_full_name() or student.username
        billing_email = (request.POST.get('billing_email') or '').strip() or student.email
        billing_phone = (request.POST.get('billing_phone') or '').strip()
        billing_address = (request.POST.get('billing_address') or '').strip()
        tuition_fee = Decimal(str(request.POST.get('tuition_fee') or '0'))
        late_registration_fee = Decimal(str(request.POST.get('late_registration_fee') or '0'))
        other_charges = Decimal(str(request.POST.get('other_charges') or '0'))
        notes = (request.POST.get('notes') or '').strip()

        if invoice is None:
            invoice = Invoice.objects.create(
                student=student,
                academic_session=academic_session,
                term=term,
                billing_name=billing_name,
                billing_email=billing_email,
                billing_phone=billing_phone,
                billing_address=billing_address,
                tuition_fee=tuition_fee,
                late_registration_fee=late_registration_fee,
                other_charges=other_charges,
                notes=notes,
                status=Invoice.Status.SENT,
            )
            invoice.itemized_charges = [
                {'title': 'Tuition Fee', 'description': 'Academic school tuition', 'amount': str(invoice.tuition_fee)},
                {'title': 'Late Registration', 'description': 'Penalty for late registration', 'amount': str(invoice.late_registration_fee)},
                {'title': 'Other Charges', 'description': notes or 'Other school charges', 'amount': str(invoice.other_charges)},
            ]
            invoice.save(update_fields=['itemized_charges'])
            message = 'Invoice created successfully.'
        else:
            invoice.student = student
            invoice.academic_session = academic_session
            invoice.term = term
            invoice.billing_name = billing_name
            invoice.billing_email = billing_email
            invoice.billing_phone = billing_phone
            invoice.billing_address = billing_address
            invoice.tuition_fee = tuition_fee
            invoice.late_registration_fee = late_registration_fee
            invoice.other_charges = other_charges
            invoice.notes = notes
            invoice.status = Invoice.Status.SENT
            invoice.itemized_charges = [
                {'title': 'Tuition Fee', 'description': 'Academic school tuition', 'amount': str(invoice.tuition_fee)},
                {'title': 'Late Registration', 'description': 'Penalty for late registration', 'amount': str(invoice.late_registration_fee)},
                {'title': 'Other Charges', 'description': notes or 'Other school charges', 'amount': str(invoice.other_charges)},
            ]
            invoice.save()
            message = 'Invoice updated successfully.'

        messages.success(request, message)
        return redirect('payments:invoice_detail', invoice_number=invoice.invoice_number)

    return render(request, 'payments/manual_invoice_entry.html', {'students': students, 'initial': initial, 'invoice': invoice})


@login_required
@user_passes_test(_can_manage_invoices)
@transaction.atomic
def bulk_invoice_entry(request):
    form = BulkInvoiceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student_class = form.cleaned_data['student_class']
        students = get_user_model().objects.filter(
            role='STUDENT',
        ).filter(
            Q(profile__student_class__name=student_class)
            | Q(profile__student_class__name__startswith=f'{student_class}-')
        ).order_by('first_name', 'last_name', 'username')
        created_count = 0
        skipped_count = 0
        data = form.cleaned_data
        itemized_charges = [
            {'title': 'Tuition Fee', 'description': 'Academic school tuition', 'amount': str(data['tuition_fee'])},
            {'title': 'Late Registration', 'description': 'Penalty for late registration', 'amount': str(data['late_registration_fee'])},
            {'title': 'Other Charges', 'description': data['notes'] or 'Other school charges', 'amount': str(data['other_charges'])},
        ]

        for student in students:
            if Invoice.objects.filter(
                student=student,
                academic_session=data['academic_session'],
                term=data['term'],
            ).exists():
                skipped_count += 1
                continue
            invoice = Invoice.objects.create(
                student=student,
                academic_session=data['academic_session'],
                term=data['term'],
                due_date=data['due_date'],
                tuition_fee=data['tuition_fee'],
                late_registration_fee=data['late_registration_fee'],
                other_charges=data['other_charges'],
                notes=data['notes'],
                status=Invoice.Status.SENT,
                itemized_charges=itemized_charges,
            )
            invoice.save(update_fields=['itemized_charges'])
            created_count += 1

        messages.success(
            request,
            f'{created_count} invoice(s) created for {student_class}. '
            f'{skipped_count} existing invoice(s) skipped.',
        )
        return redirect('payments:bulk_invoice_entry')

    return render(request, 'payments/bulk_invoice_entry.html', {'form': form})


@login_required
def student_invoice_payment(request):
    invoice = Invoice.objects.filter(student=request.user).order_by('-issue_date').first()
    if not invoice:
        messages.info(request, 'You do not have any invoice yet. Please contact the school admin.')
        return redirect('payments:dashboard')
    return render(request, 'payments/invoice_payment.html', {'invoice': invoice})


@login_required
def process_invoice_payment(request, invoice_number):
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    if not request.user.is_staff and invoice.student != request.user:
        raise Http404('Invoice not found.')

    if request.method != 'POST':
        return redirect('payments:invoice_detail', invoice_number=invoice.invoice_number)

    gateway_name = request.POST.get('gateway', 'stripe').lower()
    category = PaymentCategory.objects.filter(is_active=True).order_by('id').first()
    if category is None:
        category = PaymentCategory.objects.create(
            name='School Fees',
            amount=invoice.total_amount,
            description='School invoice settlement',
            is_active=True,
        )

    transaction = Transaction.objects.create(
        student=request.user,
        category=category,
        amount=invoice.total_amount,
        academic_session=invoice.academic_session,
        term=invoice.term,
        status=Transaction.Status.PENDING,
    )
    invoice.transaction = transaction
    invoice.status = Invoice.Status.SENT
    invoice.save(update_fields=['transaction', 'status'])

    callback_url = request.build_absolute_uri(reverse('payments:verify_payment')) + f'?reference={transaction.reference}&gateway={gateway_name}'
    service = GatewayServiceFactory.get(gateway_name)
    result = service.initialize_transaction(
        email=invoice.payer_email or request.user.email,
        amount_in_kobo=transaction.amount,
        reference=transaction.reference,
        callback_url=callback_url,
    )

    if result.get('status'):
        auth_url = result['data'].get('authorization_url') or result['data'].get('checkout_url')
        if auth_url:
            return redirect(auth_url)

    messages.error(request, 'The selected gateway is not available at the moment. Please try another payment method.')
    return redirect('payments:invoice_detail', invoice_number=invoice.invoice_number)


@login_required
def invoice_detail(request, invoice_number):
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    if not request.user.is_staff and invoice.student != request.user:
        raise Http404('Invoice not found.')
    return render(request, 'payments/invoice_detail.html', {'invoice': invoice})


@login_required
def download_invoice(request, invoice_number):
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    if not request.user.is_staff and invoice.student != request.user:
        raise Http404('Invoice not found.')

    pdf_buffer = generate_invoice_pdf(invoice)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{invoice.invoice_number}.pdf"'
    return response


@login_required
def download_receipt(request, reference):
    """Downloads a PDF receipt for a successful transaction."""
    transaction = get_object_or_404(
        Transaction,
        reference=reference,
        student=request.user,
    )

    if transaction.status != Transaction.Status.SUCCESSFUL:
        raise Http404('Receipt available only for successful payments.')

    pdf_buffer = generate_receipt_pdf(transaction)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    filename = f"Receipt-{transaction.reference[:8].upper()}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response