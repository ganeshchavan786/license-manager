"""
Unit Tests - Promo Code Service
Task 24.2: Write unit tests for promo code service (80% coverage)
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.services.promo import (
    create_promo_code,
    validate_promo_code,
    apply_promo_code,
    deactivate_promo_code
)


class TestCreatePromoCode:
    def test_create_percentage_promo(self, db, admin_user):
        result = create_promo_code(
            db=db,
            code="SAVE20",
            discount_type="percentage",
            discount_value=20,
            applicable_plans=["basic", "premium"],
            created_by=admin_user.id
        )
        assert result.code == "SAVE20"
        assert result.discount_type == "percentage"
        assert result.discount_value == 20
        assert result.is_active == True

    def test_create_fixed_promo(self, db, admin_user):
        result = create_promo_code(
            db=db,
            code="FLAT100",
            discount_type="fixed",
            discount_value=10000,
            applicable_plans=["premium"],
            created_by=admin_user.id
        )
        assert result.code == "FLAT100"
        assert result.discount_type == "fixed"

    def test_create_duplicate_code_fails(self, db, admin_user):
        create_promo_code(db=db, code="DUP", discount_type="percentage",
                         discount_value=10, applicable_plans=["basic"],
                         created_by=admin_user.id)
        with pytest.raises(Exception):
            create_promo_code(db=db, code="DUP", discount_type="percentage",
                             discount_value=10, applicable_plans=["basic"],
                             created_by=admin_user.id)

    def test_create_with_expiry(self, db, admin_user):
        expiry = datetime.now(timezone.utc) + timedelta(days=30)
        result = create_promo_code(
            db=db, code="EXPIRY30", discount_type="percentage",
            discount_value=15, applicable_plans=["basic"],
            expiry_date=expiry, created_by=admin_user.id
        )
        assert result.expiry_date is not None

    def test_create_with_usage_limit(self, db, admin_user):
        result = create_promo_code(
            db=db, code="LIMITED", discount_type="percentage",
            discount_value=10, applicable_plans=["basic"],
            usage_limit=5, created_by=admin_user.id
        )
        assert result.usage_limit == 5


class TestValidatePromoCode:
    def test_validate_valid_code(self, db, admin_user):
        create_promo_code(db=db, code="VALID10", discount_type="percentage",
                         discount_value=10, applicable_plans=["basic"],
                         created_by=admin_user.id)
        result = validate_promo_code(db=db, code="VALID10", plan="basic")
        assert result["valid"] == True
        assert result["discount_amount"] > 0

    def test_validate_invalid_code(self, db):
        result = validate_promo_code(db=db, code="NOTEXIST", plan="basic")
        assert result["valid"] == False

    def test_validate_wrong_plan(self, db, admin_user):
        create_promo_code(db=db, code="BASICONLY", discount_type="percentage",
                         discount_value=10, applicable_plans=["basic"],
                         created_by=admin_user.id)
        result = validate_promo_code(db=db, code="BASICONLY", plan="premium")
        assert result["valid"] == False

    def test_validate_expired_code(self, db, admin_user):
        future = datetime.now(timezone.utc) + timedelta(days=1)
        promo = create_promo_code(db=db, code="EXPIRED", discount_type="percentage",
                         discount_value=10, applicable_plans=["basic"],
                         expiry_date=future, created_by=admin_user.id)
        promo.expiry_date = datetime.now(timezone.utc) - timedelta(days=1)
        db.commit()
        result = validate_promo_code(db=db, code="EXPIRED", plan="basic")
        assert result["valid"] == False

    def test_validate_percentage_discount_calculation(self, db, admin_user):
        create_promo_code(db=db, code="PCT20", discount_type="percentage",
                         discount_value=20, applicable_plans=["basic"],
                         created_by=admin_user.id)
        result = validate_promo_code(db=db, code="PCT20", plan="basic")
        assert result["valid"] == True
        assert result["discount_amount"] > 0

    def test_validate_fixed_discount_calculation(self, db, admin_user):
        create_promo_code(db=db, code="FIX5000", discount_type="fixed",
                         discount_value=5000, applicable_plans=["basic"],
                         created_by=admin_user.id)
        result = validate_promo_code(db=db, code="FIX5000", plan="basic")
        assert result["valid"] == True
        assert result["discount_amount"] == 5000

    def test_validate_inactive_code(self, db, admin_user):
        promo = create_promo_code(db=db, code="INACTIVE", discount_type="percentage",
                                  discount_value=10, applicable_plans=["basic"],
                                  created_by=admin_user.id)
        deactivate_promo_code(db=db, code=promo.code)
        result = validate_promo_code(db=db, code="INACTIVE", plan="basic")
        assert result["valid"] == False


class TestDeactivatePromoCode:
    def test_deactivate_success(self, db, admin_user):
        promo = create_promo_code(db=db, code="TODEACT", discount_type="percentage",
                                  discount_value=10, applicable_plans=["basic"],
                                  created_by=admin_user.id)
        result = deactivate_promo_code(db=db, code=promo.code)
        assert result == True
        db.refresh(promo)
        assert promo.is_active == False

    def test_deactivate_nonexistent(self, db):
        with pytest.raises(Exception):
            deactivate_promo_code(db=db, code="NONEXISTENT")
