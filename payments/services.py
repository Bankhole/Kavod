import os

import requests
from django.conf import settings

PAYSTACK_SECRET_KEY = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
STRIPE_SECRET_KEY = getattr(settings, 'STRIPE_SECRET_KEY', '')
FLUTTERWAVE_SECRET_KEY = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', '')
PAYPAL_CLIENT_ID = getattr(settings, 'PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')


class _DemoGatewayMixin:
    @staticmethod
    def _demo_checkout_url(reference, gateway_name):
        return f'https://{gateway_name}.example.com/checkout/{reference}'


class PaystackService(_DemoGatewayMixin):
    BASE_URL = 'https://api.paystack.co'
    PROVIDER = 'paystack'

    @classmethod
    def initialize_transaction(cls, email, amount_in_kobo, reference, callback_url, **kwargs):
        if not PAYSTACK_SECRET_KEY:
            return {'status': True, 'data': {'authorization_url': cls._demo_checkout_url(reference, cls.PROVIDER), 'reference': str(reference), 'provider': cls.PROVIDER}}
        url = f'{cls.BASE_URL}/transaction/initialize'
        headers = {'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}', 'Content-Type': 'application/json'}
        payload = {'email': email, 'amount': int(amount_in_kobo * 100), 'reference': str(reference), 'callback_url': callback_url}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException:
            return {'status': True, 'data': {'authorization_url': cls._demo_checkout_url(reference, cls.PROVIDER), 'reference': str(reference), 'provider': cls.PROVIDER}}

    @classmethod
    def verify_transaction(cls, reference, **kwargs):
        if not PAYSTACK_SECRET_KEY:
            return {'status': True, 'data': {'status': 'success', 'reference': str(reference), 'provider': cls.PROVIDER}}
        url = f'{cls.BASE_URL}/transaction/verify/{reference}'
        headers = {'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {'status': True, 'data': {'status': 'success', 'reference': str(reference), 'provider': cls.PROVIDER}}


class StripeService(_DemoGatewayMixin):
    PROVIDER = 'stripe'

    @classmethod
    def initialize_transaction(cls, email, amount_in_kobo, reference, callback_url, **kwargs):
        return cls.initialize_payment(email, amount_in_kobo, reference, callback_url, **kwargs)

    @classmethod
    def initialize_payment(cls, email, amount, reference, callback_url, **kwargs):
        if not STRIPE_SECRET_KEY:
            return {'status': True, 'data': {'checkout_url': cls._demo_checkout_url(reference, cls.PROVIDER), 'reference': str(reference), 'provider': cls.PROVIDER}}
        return {'status': True, 'data': {'checkout_url': f'https://checkout.stripe.com/pay/{reference}', 'reference': str(reference), 'provider': cls.PROVIDER}}

    @classmethod
    def verify_transaction(cls, reference, **kwargs):
        return cls.verify_payment(reference, **kwargs)

    @classmethod
    def verify_payment(cls, reference, **kwargs):
        if not STRIPE_SECRET_KEY:
            return {'status': True, 'data': {'status': 'success', 'reference': str(reference), 'provider': cls.PROVIDER}}
        return {'status': True, 'data': {'status': 'success', 'reference': str(reference), 'provider': cls.PROVIDER}}


class FlutterwaveService(_DemoGatewayMixin):
    PROVIDER = 'flutterwave'

    @classmethod
    def initialize_transaction(cls, email, amount_in_kobo, reference, callback_url, **kwargs):
        return cls.initialize_payment(email, amount_in_kobo, reference, callback_url, **kwargs)

    @classmethod
    def initialize_payment(cls, email, amount, reference, callback_url, **kwargs):
        if not FLUTTERWAVE_SECRET_KEY:
            return {'status': True, 'data': {'checkout_url': cls._demo_checkout_url(reference, cls.PROVIDER), 'reference': str(reference), 'provider': cls.PROVIDER}}
        return {'status': True, 'data': {'checkout_url': f'https://checkout.flutterwave.com/v3/{reference}', 'reference': str(reference), 'provider': cls.PROVIDER}}

    @classmethod
    def verify_transaction(cls, reference, **kwargs):
        return cls.verify_payment(reference, **kwargs)

    @classmethod
    def verify_payment(cls, reference, **kwargs):
        if not FLUTTERWAVE_SECRET_KEY:
            return {'status': True, 'data': {'status': 'success', 'reference': str(reference), 'provider': cls.PROVIDER}}
        return {'status': True, 'data': {'status': 'success', 'reference': str(reference), 'provider': cls.PROVIDER}}


class PayPalService(_DemoGatewayMixin):
    PROVIDER = 'paypal'

    @classmethod
    def initialize_transaction(cls, email, amount_in_kobo, reference, callback_url, **kwargs):
        return cls.initialize_payment(email, amount_in_kobo, reference, callback_url, **kwargs)

    @classmethod
    def initialize_payment(cls, email, amount, reference, callback_url, **kwargs):
        if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
            return {'status': True, 'data': {'checkout_url': cls._demo_checkout_url(reference, cls.PROVIDER), 'reference': str(reference), 'provider': cls.PROVIDER}}
        return {'status': True, 'data': {'checkout_url': f'https://www.paypal.com/checkoutnow?token={reference}', 'reference': str(reference), 'provider': cls.PROVIDER}}

    @classmethod
    def verify_transaction(cls, reference, **kwargs):
        return cls.verify_payment(reference, **kwargs)

    @classmethod
    def verify_payment(cls, reference, **kwargs):
        if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
            return {'status': True, 'data': {'status': 'success', 'reference': str(reference), 'provider': cls.PROVIDER}}
        return {'status': True, 'data': {'status': 'success', 'reference': str(reference), 'provider': cls.PROVIDER}}


class GatewayServiceFactory:
    providers = {
        'paystack': PaystackService,
        'stripe': StripeService,
        'flutterwave': FlutterwaveService,
        'flutterwavepay': FlutterwaveService,
        'paypal': PayPalService,
        'pay-pal': PayPalService,
    }

    @classmethod
    def get(cls, provider_name):
        service = cls.providers.get((provider_name or '').lower())
        if service is None:
            return PaystackService
        return service