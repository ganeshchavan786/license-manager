"""
Invoice Service - Generate and manage invoices with PDF generation

This service provides functionality to:
- Generate invoices with sequential numbering
- Generate PDF invoices using reportlab
- Calculate GST (18%)
- Retrieve invoices
- Email invoices to customers
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import os
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas

from app.models import Invoice, Customer, Payment, PromoCode
from app.services.email import queue_email
from app.config import settings

logger = logging.getLogger(__name__)

# Company details
COMPANY_NAME = "SalaryPay"
COMPANY_ADDRESS = "123 Business Park, Mumbai, Maharashtra 400001"
COMPANY_GST = "27AABCS1234F1Z5"
COMPANY_EMAIL = "billing@salarypay.com"
COMPANY_PHONE = "+91 22 1234 5678"

# GST rate
GST_RATE = 18  # 18%

# Invoice directory
INVOICE_DIR = "invoices"


def _ensure_invoice_directory():
    """
    Ensure invoices directory exists
    
    Postconditions:
    - invoices/ directory exists
    """
    if not os.path.exists(INVOICE_DIR):
        os.makedirs(INVOICE_DIR)
        logger.info(f"Created invoice directory: {INVOICE_DIR}")


def _generate_invoice_number(db: Session) -> str:
    """
    Generate sequential invoice number in format INV-YYYYMM-XXXX
    
    Preconditions:
    - db session is valid
    
    Postconditions:
    - Returns unique invoice number
    - Format: INV-YYYYMM-XXXX (e.g., INV-202605-0001)
    
    Example:
    - First invoice in May 2026: INV-202605-0001
    - Second invoice in May 2026: INV-202605-0002
    - First invoice in June 2026: INV-202606-0001
    """
    now = datetime.now(timezone.utc)
    year_month = now.strftime("%Y%m")
    prefix = f"INV-{year_month}-"
    
    # Get last invoice for this month
    last_invoice = db.query(Invoice).filter(
        Invoice.invoice_number.like(f"{prefix}%")
    ).order_by(Invoice.invoice_number.desc()).first()
    
    if last_invoice:
        # Extract sequence number and increment
        last_seq = int(last_invoice.invoice_number.split("-")[-1])
        new_seq = last_seq + 1
    else:
        # First invoice of the month
        new_seq = 1
    
    invoice_number = f"{prefix}{new_seq:04d}"
    logger.info(f"Generated invoice number: {invoice_number}")
    return invoice_number


def generate_invoice(
    db: Session,
    customer_id: str,
    payment_id: str,
    plan: str,
    base_amount: int,
    discount_amount: int = 0,
    promo_code_id: Optional[str] = None
) -> Invoice:
    """
    Generate invoice for a payment
    
    Preconditions:
    - customer_id exists in customers table
    - payment_id exists in payments table
    - plan is one of: "basic", "premium"
    - base_amount is positive integer in paise
    - discount_amount is non-negative integer in paise
    
    Postconditions:
    - New Invoice record created in database
    - invoice_number is unique and sequential
    - GST calculated at 18% on (base_amount - discount_amount)
    - total_amount = base_amount - discount_amount + gst_amount
    - Returns Invoice object
    
    Example:
    - base_amount = 49900 (₹499)
    - discount_amount = 5000 (₹50)
    - taxable_amount = 44900 (₹449)
    - gst_amount = 8082 (₹80.82)
    - total_amount = 52982 (₹529.82)
    """
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    # Validate payment exists
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise ValueError("Payment not found")
    
    # Validate plan
    if plan not in ["basic", "premium"]:
        raise ValueError("Invalid plan")
    
    # Validate amounts
    if base_amount <= 0:
        raise ValueError("Base amount must be positive")
    
    if discount_amount < 0:
        raise ValueError("Discount amount cannot be negative")
    
    if discount_amount > base_amount:
        raise ValueError("Discount amount cannot exceed base amount")
    
    # Calculate GST
    taxable_amount = base_amount - discount_amount
    gst_amount = int((taxable_amount * GST_RATE) / 100)
    total_amount = taxable_amount + gst_amount
    
    # Generate invoice number
    invoice_number = _generate_invoice_number(db)
    
    # Create invoice
    invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=customer_id,
        payment_id=payment_id,
        plan=plan,
        base_amount=base_amount,
        gst_rate=GST_RATE,
        gst_amount=gst_amount,
        total_amount=total_amount,
        discount_amount=discount_amount,
        promo_code_id=promo_code_id,
        invoice_date=datetime.now(timezone.utc),
        is_emailed=False
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    logger.info(f"Invoice generated: {invoice_number} for customer {customer_id}")
    return invoice


def generate_invoice_pdf(
    db: Session,
    invoice_id: str
) -> str:
    """
    Generate PDF for an invoice
    
    Preconditions:
    - invoice_id exists in invoices table
    - invoices/ directory exists
    
    Postconditions:
    - PDF file created in invoices/ directory
    - Invoice.pdf_path updated with file path
    - Returns file path to PDF
    
    PDF Template includes:
    - Company details (name, address, GST number)
    - Customer details (business name, email, address)
    - Invoice number and date
    - Itemized breakdown (plan, base amount, discount, GST, total)
    - Payment information
    """
    # Ensure directory exists
    _ensure_invoice_directory()
    
    # Get invoice with related data
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Invoice not found")
    
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    payment = db.query(Payment).filter(Payment.id == invoice.payment_id).first()
    if not payment:
        raise ValueError("Payment not found")
    
    # Get promo code if applicable
    promo_code = None
    if invoice.promo_code_id:
        promo_code = db.query(PromoCode).filter(PromoCode.id == invoice.promo_code_id).first()
    
    # Generate PDF filename
    pdf_filename = f"{invoice.invoice_number}.pdf"
    pdf_path = os.path.join(INVOICE_DIR, pdf_filename)
    
    # Create PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1976D2'),
        spaceAfter=12
    )
    
    normal_style = styles['Normal']
    
    # Title
    story.append(Paragraph("TAX INVOICE", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Company and Customer details side by side
    details_data = [
        [
            Paragraph(f"<b>{COMPANY_NAME}</b><br/>{COMPANY_ADDRESS}<br/>GST: {COMPANY_GST}<br/>Email: {COMPANY_EMAIL}<br/>Phone: {COMPANY_PHONE}", normal_style),
            Paragraph(f"<b>Bill To:</b><br/><b>{customer.business_name}</b><br/>{customer.owner_name}<br/>{customer.email}<br/>{customer.phone}<br/>{customer.city or ''}", normal_style)
        ]
    ]
    
    details_table = Table(details_data, colWidths=[3 * inch, 3 * inch])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Invoice details
    invoice_info_data = [
        ['Invoice Number:', invoice.invoice_number],
        ['Invoice Date:', invoice.invoice_date.strftime('%d %B %Y')],
        ['Payment ID:', payment.razorpay_payment_id or 'N/A']
    ]
    
    invoice_info_table = Table(invoice_info_data, colWidths=[2 * inch, 4 * inch])
    invoice_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(invoice_info_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Itemized breakdown
    story.append(Paragraph("Invoice Details", heading_style))
    
    # Build items table
    items_data = [
        ['Description', 'Amount (₹)']
    ]
    
    # Plan subscription
    items_data.append([
        f'SalaryPay {invoice.plan.capitalize()} Plan - Monthly Subscription',
        f'{invoice.base_amount / 100:.2f}'
    ])
    
    # Discount if applicable
    if invoice.discount_amount > 0:
        discount_desc = f'Discount'
        if promo_code:
            discount_desc += f' (Promo: {promo_code.code})'
        items_data.append([
            discount_desc,
            f'-{invoice.discount_amount / 100:.2f}'
        ])
    
    # Subtotal
    subtotal = invoice.base_amount - invoice.discount_amount
    items_data.append([
        'Subtotal',
        f'{subtotal / 100:.2f}'
    ])
    
    # GST
    items_data.append([
        f'GST ({invoice.gst_rate}%)',
        f'{invoice.gst_amount / 100:.2f}'
    ])
    
    # Total
    items_data.append([
        'Total Amount',
        f'{invoice.total_amount / 100:.2f}'
    ])
    
    items_table = Table(items_data, colWidths=[4 * inch, 2 * inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
        
        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F5E9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
        
        # All cells
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.5 * inch))
    
    # Footer
    footer_text = """
    <b>Payment Terms:</b> Payment is due immediately upon receipt of this invoice.<br/>
    <b>Thank you for your business!</b><br/><br/>
    This is a computer-generated invoice and does not require a signature.
    """
    story.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(story)
    
    # Update invoice with PDF path
    invoice.pdf_path = pdf_path
    db.commit()
    
    logger.info(f"PDF generated for invoice {invoice.invoice_number}: {pdf_path}")
    return pdf_path


def get_invoice(
    db: Session,
    invoice_id: str,
    customer_id: Optional[str] = None
) -> Optional[Invoice]:
    """
    Get invoice by ID
    
    Preconditions:
    - invoice_id is valid UUID
    - If customer_id provided, must match invoice's customer_id
    
    Postconditions:
    - Returns Invoice object if found and authorized
    - Returns None if not found or unauthorized
    """
    query = db.query(Invoice).filter(Invoice.id == invoice_id)
    
    # If customer_id provided, ensure customer can only access their invoices
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    
    invoice = query.first()
    return invoice


def get_customer_invoices(
    db: Session,
    customer_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[Invoice]:
    """
    Get all invoices for a customer
    
    Preconditions:
    - customer_id exists in customers table
    - limit is positive integer
    - offset is non-negative integer
    
    Postconditions:
    - Returns list of Invoice objects ordered by invoice_date descending
    - Returns empty list if no invoices found
    - Maximum of 'limit' invoices returned
    """
    invoices = db.query(Invoice).filter(
        Invoice.customer_id == customer_id
    ).order_by(
        Invoice.invoice_date.desc()
    ).limit(limit).offset(offset).all()
    
    return invoices


def email_invoice(
    db: Session,
    invoice_id: str
) -> bool:
    """
    Email invoice PDF to customer
    
    Preconditions:
    - invoice_id exists in invoices table
    - Invoice has pdf_path set
    - PDF file exists at pdf_path
    
    Postconditions:
    - Email queued with invoice PDF attachment
    - Invoice.is_emailed set to True
    - Returns True if successful
    """
    # Get invoice with related data
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Invoice not found")
    
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    # Check if PDF exists
    if not invoice.pdf_path:
        raise ValueError("Invoice PDF not generated")
    
    if not os.path.exists(invoice.pdf_path):
        raise ValueError("Invoice PDF file not found")
    
    # Create email body
    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2E7D32; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .invoice-details {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #2E7D32; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Invoice from SalaryPay</h1>
        </div>
        <div class="content">
            <p>Hi {customer.owner_name},</p>
            
            <p>Thank you for your payment! Please find your invoice attached.</p>
            
            <div class="invoice-details">
                <p><strong>Invoice Number:</strong> {invoice.invoice_number}</p>
                <p><strong>Invoice Date:</strong> {invoice.invoice_date.strftime('%d %B %Y')}</p>
                <p><strong>Plan:</strong> {invoice.plan.capitalize()}</p>
                <p><strong>Amount:</strong> ₹{invoice.total_amount / 100:.2f}</p>
            </div>
            
            <p>You can also download your invoice anytime from your dashboard.</p>
            
            <p>Thank you for choosing SalaryPay!</p>
        </div>
        <div class="footer">
            <p>SalaryPay - Salary Management Made Easy</p>
            <p>Need help? Contact us at {settings.SUPPORT_EMAIL}</p>
        </div>
    </div>
</body>
</html>
    """
    
    body_text = f"""
Hi {customer.owner_name},

Thank you for your payment! Please find your invoice attached.

Invoice Number: {invoice.invoice_number}
Invoice Date: {invoice.invoice_date.strftime('%d %B %Y')}
Plan: {invoice.plan.capitalize()}
Amount: ₹{invoice.total_amount / 100:.2f}

You can also download your invoice anytime from your dashboard.

Thank you for choosing SalaryPay!

Need help? Contact us at {settings.SUPPORT_EMAIL}
    """
    
    # Queue email with attachment
    # Note: Attachment support needs to be implemented in email service
    queue_email(
        db=db,
        to_email=customer.email,
        subject=f"Invoice {invoice.invoice_number} from SalaryPay",
        body_html=body_html,
        body_text=body_text,
        attachments=[invoice.pdf_path]
    )
    
    # Mark as emailed
    invoice.is_emailed = True
    db.commit()
    
    logger.info(f"Invoice {invoice.invoice_number} emailed to {customer.email}")
    return True
