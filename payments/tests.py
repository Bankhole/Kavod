from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

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
