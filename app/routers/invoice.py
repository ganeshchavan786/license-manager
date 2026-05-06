"""
Invoice API Endpoints

Provides REST API endpoints for:
- Listing customer invoices (customer auth)
- Retrieving invoice details (customer auth)
- Downloading invoice PDFs (customer auth)
- Emailing invoices (customer auth)
- Admin invoice management (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import os
import logging

from app.database import get_db
from app.services.auth import get_current_customer, get_current_admin
from app.services import invoice as invoice_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoices", tags=["invoices"])


# Request/Response Models

class InvoiceInfo(BaseModel):
    id: str
    invoice_number: str
    invoice_date: str
    plan: str
    base_amount: int
    discount_amount: int
    gst_rate: int
    gst_amount: int
    total_amount: int
    is_emailed: bool
    pdf_available: bool


class InvoiceListResponse(BaseModel):
    invoices: List[InvoiceInfo]
    total: int


class InvoiceDetailResponse(BaseModel):
    id: str
    invoice_number: str
    invoice_date: str
    customer_id: str
    payment_id: str
    plan: str
    base_amount: int
    discount_amount: int
    gst_rate: int
    gst_amount: int
    total_amount: int
    promo_code_id: Optional[str] = None
    is_emailed: bool
    pdf_path: Optional[str] = None
    created_at: str


class EmailInvoiceResponse(BaseModel):
    success: bool
    message: str


# Customer Endpoints

@router.get("/list", response_model=InvoiceListResponse)
def list_customer_invoices(
    limit: int = 50,
    offset: int = 0,
    customer_id: str = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get list of invoices for authenticated customer
    
    - **limit**: Maximum number of invoices to return (default: 50)
    - **offset**: Number of invoices to skip (default: 0)
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset must be non-negative")
    
    try:
        invoices = invoice_service.get_customer_invoices(
            db=db,
            customer_id=customer_id,
            limit=limit,
            offset=offset
        )
        
        invoice_list = []
        for inv in invoices:
            invoice_list.append(InvoiceInfo(
                id=inv.id,
                invoice_number=inv.invoice_number,
                invoice_date=inv.invoice_date.isoformat(),
                plan=inv.plan,
                base_amount=inv.base_amount,
                discount_amount=inv.discount_amount,
                gst_rate=inv.gst_rate,
                gst_amount=inv.gst_amount,
                total_amount=inv.total_amount,
                is_emailed=inv.is_emailed,
                pdf_available=inv.pdf_path is not None and os.path.exists(inv.pdf_path)
            ))
        
        return InvoiceListResponse(
            invoices=invoice_list,
            total=len(invoice_list)
        )
    except Exception as e:
        logger.error(f"Failed to list invoices for customer {customer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list invoices: {str(e)}")


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
def get_invoice_details(
    invoice_id: str,
    customer_id: str = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific invoice
    
    - **invoice_id**: ID of the invoice
    """
    try:
        invoice = invoice_service.get_invoice(
            db=db,
            invoice_id=invoice_id,
            customer_id=customer_id
        )
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return InvoiceDetailResponse(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date.isoformat(),
            customer_id=invoice.customer_id,
            payment_id=invoice.payment_id,
            plan=invoice.plan,
            base_amount=invoice.base_amount,
            discount_amount=invoice.discount_amount,
            gst_rate=invoice.gst_rate,
            gst_amount=invoice.gst_amount,
            total_amount=invoice.total_amount,
            promo_code_id=invoice.promo_code_id,
            is_emailed=invoice.is_emailed,
            pdf_path=invoice.pdf_path,
            created_at=invoice.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get invoice: {str(e)}")


@router.get("/{invoice_id}/download")
def download_invoice_pdf(
    invoice_id: str,
    customer_id: str = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Download invoice PDF
    
    - **invoice_id**: ID of the invoice
    """
    try:
        invoice = invoice_service.get_invoice(
            db=db,
            invoice_id=invoice_id,
            customer_id=customer_id
        )
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Check if PDF exists
        if not invoice.pdf_path:
            raise HTTPException(status_code=404, detail="Invoice PDF not generated")
        
        if not os.path.exists(invoice.pdf_path):
            raise HTTPException(status_code=404, detail="Invoice PDF file not found")
        
        # Return PDF file
        return FileResponse(
            path=invoice.pdf_path,
            media_type="application/pdf",
            filename=f"{invoice.invoice_number}.pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download invoice: {str(e)}")


@router.post("/{invoice_id}/email", response_model=EmailInvoiceResponse)
def email_invoice_to_customer(
    invoice_id: str,
    customer_id: str = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Email invoice PDF to customer
    
    - **invoice_id**: ID of the invoice
    """
    try:
        invoice = invoice_service.get_invoice(
            db=db,
            invoice_id=invoice_id,
            customer_id=customer_id
        )
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Email invoice
        success = invoice_service.email_invoice(db=db, invoice_id=invoice_id)
        
        if success:
            return EmailInvoiceResponse(
                success=True,
                message=f"Invoice {invoice.invoice_number} has been emailed successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to email invoice")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to email invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to email invoice: {str(e)}")


# Admin Endpoints

@router.get("/admin/list", response_model=InvoiceListResponse)
def list_all_invoices_admin(
    limit: int = 50,
    offset: int = 0,
    customer_id: Optional[str] = None,
    admin_payload: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all invoices (Admin only)
    
    - **limit**: Maximum number of invoices to return (default: 50)
    - **offset**: Number of invoices to skip (default: 0)
    - **customer_id**: Optional filter by customer ID
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset must be non-negative")
    
    try:
        from app.models import Invoice
        
        query = db.query(Invoice)
        
        # Filter by customer if provided
        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)
        
        # Get invoices
        invoices = query.order_by(
            Invoice.invoice_date.desc()
        ).limit(limit).offset(offset).all()
        
        invoice_list = []
        for inv in invoices:
            invoice_list.append(InvoiceInfo(
                id=inv.id,
                invoice_number=inv.invoice_number,
                invoice_date=inv.invoice_date.isoformat(),
                plan=inv.plan,
                base_amount=inv.base_amount,
                discount_amount=inv.discount_amount,
                gst_rate=inv.gst_rate,
                gst_amount=inv.gst_amount,
                total_amount=inv.total_amount,
                is_emailed=inv.is_emailed,
                pdf_available=inv.pdf_path is not None and os.path.exists(inv.pdf_path)
            ))
        
        return InvoiceListResponse(
            invoices=invoice_list,
            total=len(invoice_list)
        )
    except Exception as e:
        logger.error(f"Failed to list invoices (admin): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list invoices: {str(e)}")


@router.post("/admin/{invoice_id}/regenerate")
def regenerate_invoice_pdf_admin(
    invoice_id: str,
    admin_payload: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Regenerate invoice PDF (Admin only)
    
    - **invoice_id**: ID of the invoice
    """
    try:
        from app.models import Invoice
        
        # Check if invoice exists
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Regenerate PDF
        pdf_path = invoice_service.generate_invoice_pdf(db=db, invoice_id=invoice_id)
        
        return {
            "success": True,
            "message": f"Invoice PDF regenerated successfully",
            "invoice_number": invoice.invoice_number,
            "pdf_path": pdf_path
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to regenerate invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate invoice: {str(e)}")


@router.get("/admin/{invoice_id}/download")
def download_invoice_pdf_admin(
    invoice_id: str,
    admin_payload: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Download invoice PDF (Admin only - no customer restriction)
    
    - **invoice_id**: ID of the invoice
    """
    try:
        from app.models import Invoice
        
        # Get invoice without customer restriction
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Check if PDF exists
        if not invoice.pdf_path:
            raise HTTPException(status_code=404, detail="Invoice PDF not generated")
        
        if not os.path.exists(invoice.pdf_path):
            raise HTTPException(status_code=404, detail="Invoice PDF file not found")
        
        # Return PDF file
        return FileResponse(
            path=invoice.pdf_path,
            media_type="application/pdf",
            filename=f"{invoice.invoice_number}.pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download invoice: {str(e)}")
