import io
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _invoice_styles():
    styles = getSampleStyleSheet()
    return {
        'title': ParagraphStyle('SchoolTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#0F172A'), bold=True),
        'subtitle': ParagraphStyle('ReceiptSubtitle', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.HexColor('#64748B')),
        'bold': ParagraphStyle('BoldLabel', parent=styles['Normal'], fontSize=10, leading=14, fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A')),
        'body': ParagraphStyle('ValueText', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155')),
        'amount': ParagraphStyle('AmountText', parent=styles['Normal'], fontSize=11, leading=16, fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A'), alignment=2),
        'status': ParagraphStyle('StatusPaid', parent=styles['Normal'], fontSize=12, leading=16, fontName='Helvetica-Bold', textColor=colors.HexColor('#166534'), alignment=2),
    }


def generate_receipt_pdf(transaction):
    """Generate a standard school payment receipt PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = _invoice_styles()
    elements = []

    header_data = [
        [
            Paragraph('NEXUS ONE ACADEMY', styles['title']),
            Paragraph('OFFICIAL RECEIPT', ParagraphStyle('RightTitle', parent=styles['title'], alignment=2, textColor=colors.HexColor('#2563EB'))),
        ],
        [
            Paragraph('12 School Road, Lekki Phase I, Lagos<br/>support@nexusoneacademy.edu.ng | +234 800 000 0000', styles['subtitle']),
            Paragraph(f'<b>Receipt No:</b> {transaction.reference[:12].upper()}', ParagraphStyle('RightRef', parent=styles['subtitle'], alignment=2)),
        ],
    ]
    header_table = Table(header_data, colWidths=[4.0 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=15))

    meta_data = [
        [Paragraph('Payer Details:', styles['bold']), Paragraph('Payment Metadata:', styles['bold'])],
        [
            Paragraph(f"<b>Name:</b> {transaction.student.get_full_name() or transaction.student.username}<br/><b>Email:</b> {transaction.student.email}", styles['body']),
            Paragraph(f"<b>Date:</b> {transaction.updated_at.strftime('%B %d, %Y - %I:%M %p')}<br/><b>Academic Session:</b> {transaction.academic_session}<br/><b>Term:</b> {transaction.term}", styles['body']),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[3.75 * inch, 3.75 * inch])
    meta_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    elements.append(meta_table)
    elements.append(Spacer(1, 22))

    table_data = [
        [Paragraph('Item Description', styles['bold']), Paragraph('Category', styles['bold']), Paragraph('Amount', ParagraphStyle('RightBold', parent=styles['bold'], alignment=2))],
        [Paragraph(f"{transaction.category.name}", styles['body']), Paragraph('School Fees / Administrative', styles['body']), Paragraph(f"₦{transaction.amount:,.2f}", ParagraphStyle('RightVal', parent=styles['body'], alignment=2))],
        [Paragraph('<b>Total Amount Paid</b>', styles['bold']), Paragraph('', styles['body']), Paragraph(f"<b>₦{transaction.amount:,.2f}</b>", ParagraphStyle('RightTotal', parent=styles['bold'], alignment=2, fontSize=11))],
    ]
    item_table = Table(table_data, colWidths=[3.5 * inch, 2.25 * inch, 1.75 * inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#0F172A')),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 25))

    footer_data = [
        [Paragraph('<b>Payment Status:</b> <font color="#166534">COMPLETED / SUCCESSFUL</font>', styles['body']), Paragraph('PAID', styles['status'])],
        [Paragraph('<i>This is a computer-generated receipt and requires no physical signature.</i>', styles['subtitle']), Paragraph('', styles['subtitle'])],
    ]
    footer_table = Table(footer_data, colWidths=[5.0 * inch, 2.5 * inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0FDF4')),
        ('BOX', (0, 0), (-1, 0), 1, colors.HexColor('#BBF7D0')),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('LEFTPADDING', (0, 0), (-1, 0), 10),
        ('RIGHTPADDING', (0, 0), (-1, 0), 10),
    ]))
    elements.append(footer_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_invoice_pdf(invoice):
    """Generate a detailed school invoice with billing details, late fee, and countdown context."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = _invoice_styles()
    elements = []

    header_data = [
        [
            Paragraph('NEXUS ONE ACADEMY', styles['title']),
            Paragraph('SCHOOL INVOICE', ParagraphStyle('RightTitle', parent=styles['title'], alignment=2, textColor=colors.HexColor('#2563EB'))),
        ],
        [
            Paragraph('12 School Road, Lekki Phase I, Lagos<br/>support@nexusoneacademy.edu.ng | +234 800 000 0000', styles['subtitle']),
            Paragraph(f'<b>Invoice No:</b> {invoice.invoice_number}<br/><b>Due Date:</b> {invoice.due_date}', ParagraphStyle('RightRef', parent=styles['subtitle'], alignment=2)),
        ],
    ]
    header_table = Table(header_data, colWidths=[4.0 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
    elements.append(header_table)
    elements.append(Spacer(1, 18))
    elements.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=15))

    student_data = [
        [Paragraph('Student Information', styles['bold']), Paragraph('Billing Details', styles['bold'])],
        [
            Paragraph(
                f"<b>Name:</b> {invoice.student_name}<br/>"
                f"<b>Email:</b> {invoice.billing_email or invoice.student.email}<br/>"
                f"<b>Phone:</b> {invoice.student_phone or 'N/A'}<br/>"
                f"<b>Address:</b> {invoice.student_address or 'N/A'}",
                styles['body'],
            ),
            Paragraph(
                f"<b>Academic Session:</b> {invoice.academic_session}<br/>"
                f"<b>Term:</b> {invoice.term}<br/>"
                f"<b>Invoice Date:</b> {invoice.issue_date.strftime('%B %d, %Y')}<br/>"
                f"<b>Countdown:</b> {invoice.remaining_days} days remaining",
                styles['body'],
            ),
        ],
    ]
    student_table = Table(student_data, colWidths=[3.75 * inch, 3.75 * inch])
    student_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    elements.append(student_table)
    elements.append(Spacer(1, 20))

    line_items = [
        [Paragraph('Item', styles['bold']), Paragraph('Details', styles['bold']), Paragraph('Amount', ParagraphStyle('RightBold', parent=styles['bold'], alignment=2))],
    ]
    for item in invoice.itemized_charges or []:
        title = item.get('title', 'Charge')
        detail = item.get('description', '')
        amount = Decimal(str(item.get('amount', '0.00')))
        line_items.append([Paragraph(title, styles['body']), Paragraph(detail, styles['body']), Paragraph(f'₦{amount:,.2f}', ParagraphStyle('RightVal', parent=styles['body'], alignment=2))])

    if invoice.tuition_fee:
        line_items.append([Paragraph('Tuition Fee', styles['body']), Paragraph('Main school tuition', styles['body']), Paragraph(f'₦{invoice.tuition_fee:,.2f}', ParagraphStyle('RightVal', parent=styles['body'], alignment=2))])
    if invoice.late_registration_fee:
        line_items.append([Paragraph('Late Registration', styles['body']), Paragraph('Service charge for late registration', styles['body']), Paragraph(f'₦{invoice.late_registration_fee:,.2f}', ParagraphStyle('RightVal', parent=styles['body'], alignment=2))])
    if invoice.other_charges:
        line_items.append([Paragraph('Other Charges', styles['body']), Paragraph(invoice.notes or 'Other school fees', styles['body']), Paragraph(f'₦{invoice.other_charges:,.2f}', ParagraphStyle('RightVal', parent=styles['body'], alignment=2))])

    line_items.append([Paragraph('<b>Total Amount Due</b>', styles['bold']), Paragraph('', styles['body']), Paragraph(f'<b>₦{invoice.total_amount:,.2f}</b>', ParagraphStyle('RightTotal', parent=styles['bold'], alignment=2, fontSize=11))])

    charge_table = Table(line_items, colWidths=[2.4 * inch, 3.0 * inch, 1.7 * inch])
    charge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#0F172A')),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(charge_table)
    elements.append(Spacer(1, 18))

    footer_data = [
        [Paragraph(f'<b>Invoice Status:</b> {invoice.get_status_display()}', styles['body']), Paragraph(f'Payment Due In: {invoice.remaining_days} Days', styles['status'])],
        [Paragraph('<i>Late registration charges apply where the student registers after the closing date.</i>', styles['subtitle']), Paragraph('', styles['subtitle'])],
    ]
    footer_table = Table(footer_data, colWidths=[5.0 * inch, 2.5 * inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FEF3C7')),
        ('BOX', (0, 0), (-1, 0), 1, colors.HexColor('#FCD34D')),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('LEFTPADDING', (0, 0), (-1, 0), 10),
        ('RIGHTPADDING', (0, 0), (-1, 0), 10),
    ]))
    elements.append(footer_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
