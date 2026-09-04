from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_dashboard, name='dashboard'),
    path('dashboard/', views.payment_dashboard, name='dashboard_alt'),
    path('pay/<int:category_id>/', views.initiate_payment, name='initiate_payment'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('history/', views.payment_history, name='history'),
    path('invoices/add/', views.manual_invoice_entry, name='manual_invoice_entry'),
    path('invoices/<str:invoice_number>/edit/', views.manual_invoice_entry, name='edit_invoice'),
    path('invoice-pay/', views.student_invoice_payment, name='invoice_payment'),
    path('invoice/<str:invoice_number>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<str:invoice_number>/pay/', views.process_invoice_payment, name='process_invoice_payment'),
    path('invoice/<str:invoice_number>/download/', views.download_invoice, name='download_invoice'),
    path('receipt/<str:reference>/', views.download_receipt, name='download_receipt'),
]