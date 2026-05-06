"""
Integration Tests - Invoice API Endpoints
Task 25.3: Write integration test for invoice generation flow
"""
import pytest


class TestCustomerInvoiceEndpoints:
    def test_list_invoices(self, client, customer_token_module):
        response = client.get(
            "/api/invoices/list",
            headers={"Authorization": f"Bearer {customer_token_module}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "invoices" in data

    def test_list_invoices_no_auth(self, client):
        response = client.get("/api/invoices/list")
        assert response.status_code == 401

    def test_get_nonexistent_invoice(self, client, customer_token_module):
        response = client.get(
            "/api/invoices/nonexistent-id",
            headers={"Authorization": f"Bearer {customer_token_module}"}
        )
        assert response.status_code == 404


class TestAdminInvoiceEndpoints:
    def test_admin_list_invoices(self, client, admin_token_module):
        response = client.get(
            "/api/invoices/admin/list",
            headers={"Authorization": f"Bearer {admin_token_module}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "invoices" in data

    def test_admin_list_no_auth(self, client):
        response = client.get("/api/invoices/admin/list")
        assert response.status_code == 401
