"""
Integration Tests - Promo Code API Endpoints
Task 25.1: Write integration test for promo code checkout flow
"""
import pytest


class TestPromoValidateEndpoint:
    def test_validate_valid_code(self, client, admin_token_module):
        # Create promo first
        client.post(
            "/api/promo/admin/create",
            json={"code": "INTTEST20", "discount_type": "percentage",
                  "discount_value": 20, "applicable_plans": ["basic", "premium"],
                  "is_multi_use": True},
            headers={"Authorization": f"Bearer {admin_token_module}"}
        )
        response = client.post(
            "/api/promo/validate",
            json={"code": "INTTEST20", "plan": "basic"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["discount_amount"] > 0

    def test_validate_invalid_code(self, client):
        response = client.post(
            "/api/promo/validate",
            json={"code": "DOESNOTEXIST", "plan": "basic"}
        )
        assert response.status_code == 200
        assert response.json()["valid"] == False

    def test_validate_wrong_plan(self, client, admin_token_module):
        client.post(
            "/api/promo/admin/create",
            json={"code": "BASICONLY2", "discount_type": "percentage",
                  "discount_value": 10, "applicable_plans": ["basic"],
                  "is_multi_use": True},
            headers={"Authorization": f"Bearer {admin_token_module}"}
        )
        # premium plan - code only valid for basic
        response = client.post(
            "/api/promo/validate",
            json={"code": "BASICONLY2", "plan": "premium"}
        )
        assert response.status_code == 200
        assert response.json()["valid"] == False


class TestAdminPromoEndpoints:
    def test_create_promo_success(self, client, admin_token_module):
        response = client.post(
            "/api/promo/admin/create",
            json={"code": "NEWCODE99", "discount_type": "percentage",
                  "discount_value": 15, "applicable_plans": ["basic"],
                  "is_multi_use": True},
            headers={"Authorization": f"Bearer {admin_token_module}"}
        )
        assert response.status_code == 200

    def test_create_promo_no_auth(self, client):
        response = client.post(
            "/api/promo/admin/create",
            json={"code": "NOAUTH99", "discount_type": "percentage",
                  "discount_value": 10, "applicable_plans": ["basic"]}
        )
        assert response.status_code == 401

    def test_list_promos(self, client, admin_token_module):
        response = client.get(
            "/api/promo/admin/list",
            headers={"Authorization": f"Bearer {admin_token_module}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "promo_codes" in data
