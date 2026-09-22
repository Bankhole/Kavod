from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from attendance.models import StudentClass

from .forms import BulkInvoiceForm, GRADE_CHOICES
from .models import Invoice


class PaymentsViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='accountant',
            email='accountant@example.com',
            password='secret123',
        )
        self.user.profile.phone_number = '08030000000'
        self.user.profile.address = '12 Muri Okunola Road'
        self.user.profile.city = 'Lagos'
        self.user.profile.state = 'Lagos State'
        self.user.profile.country = 'Nigeria'
        self.user.profile.save()

    def test_payments_dashboard_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/payments/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payments')

    def test_invoice_populates_contact_details_and_countdown_text(self):
        invoice = Invoice.objects.create(
            student=self.user,
            academic_session='2025/2026',
            term='1st',
            due_date=date.today() + timedelta(days=2),
            tuition_fee=Decimal('250000.00'),
            itemized_charges=[
                {'title': 'Tuition Fee', 'description': 'School fee', 'amount': '250000.00'}
            ],
        )

        self.assertIn('08030000000', invoice.billing_phone)
        self.assertIn('12 Muri Okunola Road', invoice.billing_address)
        self.assertIn('left', invoice.countdown_display)
        self.assertTrue('day' in invoice.countdown_display or 'hour' in invoice.countdown_display)

    def test_staff_can_create_and_repeat_bulk_class_invoices_without_duplicates(self):
        student_class = StudentClass.objects.create(name='Grade 10-A')
        staff = self.user
        staff.is_staff = True
        staff.save(update_fields=['is_staff'])
        for username in ('student_one', 'student_two'):
            student = get_user_model().objects.create_user(
                username=username,
                email=f'{username}@example.com',
                role='STUDENT',
            )
            student.profile.student_class = student_class
            student.profile.save(update_fields=['student_class'])

        self.client.force_login(staff)
        payload = {
            'student_class': 'Grade 10',
            'academic_session': '2026/2027',
            'term': '1st',
            'due_date': (date.today() + timedelta(days=30)).isoformat(),
            'tuition_fee': '250000.00',
            'late_registration_fee': '0',
            'other_charges': '5000.00',
            'notes': 'First term fees',
        }

        response = self.client.post('/payments/invoices/bulk-add/', payload)
        self.assertRedirects(response, '/payments/invoices/bulk-add/')
        self.assertEqual(Invoice.objects.filter(academic_session='2026/2027', term='1st').count(), 2)

        self.client.post('/payments/invoices/bulk-add/', payload)
        self.assertEqual(Invoice.objects.filter(academic_session='2026/2027', term='1st').count(), 2)

    def test_bulk_invoice_form_offers_grades_one_to_twelve(self):
        self.assertEqual(BulkInvoiceForm().fields['student_class'].choices, GRADE_CHOICES)
        self.assertEqual(GRADE_CHOICES[0], ('Grade 1', 'Grade 1'))
        self.assertEqual(GRADE_CHOICES[-1], ('Grade 12', 'Grade 12'))

    def test_unpaid_overdue_invoice_gets_one_surcharge(self):
        invoice = Invoice.objects.create(
            student=self.user,
            academic_session='2025/2026',
            term='1st',
            due_date=date.today() - timedelta(days=1),
            tuition_fee=Decimal('100000.00'),
            status=Invoice.Status.SENT,
        )

        self.assertEqual(invoice.overdue_fee, Decimal('5000.00'))
        self.assertEqual(invoice.total_amount, Decimal('105000.00'))
        self.assertEqual(invoice.status, Invoice.Status.OVERDUE)

        invoice.save()
        invoice.refresh_from_db()
        self.assertEqual(invoice.overdue_fee, Decimal('5000.00'))
        self.assertEqual(invoice.itemized_charges[-1]['title'], 'Overdue Surcharge')

    def test_paid_overdue_invoice_does_not_get_surcharge(self):
        invoice = Invoice.objects.create(
            student=self.user,
            academic_session='2025/2026',
            term='1st',
            due_date=date.today() - timedelta(days=1),
            tuition_fee=Decimal('100000.00'),
            status=Invoice.Status.PAID,
        )

        self.assertEqual(invoice.overdue_fee, Decimal('0.00'))
        self.assertEqual(invoice.total_amount, Decimal('100000.00'))
