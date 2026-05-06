"""
Unit Tests - Invoice Service
Task 24.4: Write unit tests for invoice service (80% coverage)
"""
import pytest
from app.services.invoice import (
    generate_invoice,
    get_invoice,
    get_customer_invoices
)
from app.models import Payment


@pytest.fixture
def sample_payment(db, sample_customer):
    payment = Payment(
        id="test-payment-001",
        customer_id=sample_customer.id,
        razorpay_payment_id="pay_test001",
        razorpay_order_id="order_test001",
        plan="basic",
        amount=49900,
        currency="INR",
        status="captured"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


class TestGenerateInvoice:
    def test_generate_invoice_basic(self, db, sample_customer, sample_payment):
        invoice = generate_invoice(
            db=db,
            customer_id=sample_customer.id,
            payment_id=sample_payment.id,
            plan="basic",
            base_amount=49900
        )
        assert invoice is not None
        assert invoice.customer_id == sample_customer.id
        assert invoice.payment_id == sample_payment.id
        assert invoice.plan == "basic"

    def test_invoice_number_format(self, db, sample_customer, sample_payment):
        invoice = generate_invoice(
            db=db,
            customer_id=sample_customer.id,
            payment_id=sample_payment.id,
            plan="basic",
            base_amount=49900
        )
        assert invoice.invoice_number.startswith("INV-")
        parts = invoice.invoice_number.split("-")
        assert len(parts) == 3

    def test_invoice_gst_calculation(self, db, sample_customer, sample_payment):
        invoice = generate_invoice(
            db=db,
            customer_id=sample_customer.id,
            payment_id=sample_payment.id,
            plan="basic",
            base_amount=49900
        )
        assert invoice.gst_rate == 18
        assert invoice.gst_amount > 0
        assert invoice.total_amount == invoice.base_amount + invoice.gst_amount

    def test_invoice_with_discount(self, db, sample_customer, sample_payment):
        invoice = generate_invoice(
            db=db,
            customer_id=sample_customer.id,
            payment_id=sample_payment.id,
            plan="basic",
            base_amount=49900,
            discount_amount=5000
        )
        assert invoice.discount_amount == 5000

    def test_sequential_invoice_numbers(self, db, sample_customer):
        p1 = Payment(id="pay-seq-1", customer_id=sample_customer.id,
                     razorpay_payment_id="pay_s1", plan="basic",
                     amount=49900, status="captured")
        p2 = Payment(id="pay-seq-2", customer_id=sample_customer.id,
                     razorpay_payment_id="pay_s2", plan="basic",
                     amount=49900, status="captured")
        db.add_all([p1, p2])
        db.commit()

        inv1 = generate_invoice(db=db, customer_id=sample_customer.id,
                                payment_id=p1.id, plan="basic", base_amount=49900)
        inv2 = generate_invoice(db=db, customer_id=sample_customer.id,
                                payment_id=p2.id, plan="basic", base_amount=49900)
        assert inv1.invoice_number != inv2.invoice_number


class TestGetInvoice:
    def test_get_existing_invoice(self, db, sample_customer, sample_payment):
        invoice = generate_invoice(db=db, customer_id=sample_customer.id,
                                   payment_id=sample_payment.id,
                                   plan="basic", base_amount=49900)
        result = get_invoice(db=db, invoice_id=invoice.id,
                             customer_id=sample_customer.id)
        assert result is not None
        assert result.id == invoice.id

    def test_get_nonexistent_invoice(self, db, sample_customer):
        result = get_invoice(db=db, invoice_id="nonexistent",
                             customer_id=sample_customer.id)
        assert result is None

    def test_get_invoice_wrong_customer(self, db, sample_customer, sample_payment):
        invoice = generate_invoice(db=db, customer_id=sample_customer.id,
                                   payment_id=sample_payment.id,
                                   plan="basic", base_amount=49900)
        result = get_invoice(db=db, invoice_id=invoice.id,
                             customer_id="wrong-customer")
        assert result is None


class TestGetCustomerInvoices:
    def test_get_invoices_empty(self, db, sample_customer):
        result = get_customer_invoices(db=db, customer_id=sample_customer.id)
        assert result == []

    def test_get_invoices_with_data(self, db, sample_customer):
        p1 = Payment(id="inv-pay-1", customer_id=sample_customer.id,
                     razorpay_payment_id="pay_i1", plan="basic",
                     amount=49900, status="captured")
        p2 = Payment(id="inv-pay-2", customer_id=sample_customer.id,
                     razorpay_payment_id="pay_i2", plan="premium",
                     amount=99900, status="captured")
        db.add_all([p1, p2])
        db.commit()

        generate_invoice(db=db, customer_id=sample_customer.id,
                        payment_id=p1.id, plan="basic", base_amount=49900)
        generate_invoice(db=db, customer_id=sample_customer.id,
                        payment_id=p2.id, plan="premium", base_amount=99900)

        result = get_customer_invoices(db=db, customer_id=sample_customer.id)
        assert len(result) == 2
