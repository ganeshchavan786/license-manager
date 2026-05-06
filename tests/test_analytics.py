"""
Unit Tests - Analytics Service
Task 24.1: Write unit tests for analytics service (80% coverage)
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.services.analytics import (
    track_usage,
    get_customer_usage,
    get_feature_stats,
    get_analytics_dashboard,
    generate_monthly_report,
    get_admin_analytics_overview
)
from app.models import UsageAnalytics


class TestTrackUsage:
    def test_track_usage_success(self, db, sample_customer, sample_license):
        result = track_usage(
            db=db,
            customer_id=sample_customer.id,
            feature_name="test_feature",
            metadata={"key": "value"}
        )
        assert result is not None
        assert result.customer_id == sample_customer.id
        assert result.feature_name == "test_feature"

    def test_track_usage_invalid_customer(self, db):
        result = track_usage(
            db=db,
            customer_id="non-existent-id",
            feature_name="test_feature"
        )
        # Should return None (non-blocking)
        assert result is None

    def test_track_usage_no_metadata(self, db, sample_customer, sample_license):
        result = track_usage(
            db=db,
            customer_id=sample_customer.id,
            feature_name="feature_no_meta"
        )
        assert result is not None
        assert result.meta_data is None

    def test_track_usage_with_ip(self, db, sample_customer, sample_license):
        result = track_usage(
            db=db,
            customer_id=sample_customer.id,
            feature_name="feature_with_ip",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        assert result.ip_address == "192.168.1.1"
        assert result.user_agent == "Mozilla/5.0"

    def test_track_multiple_features(self, db, sample_customer, sample_license):
        features = ["login", "export", "report", "salary"]
        for f in features:
            track_usage(db=db, customer_id=sample_customer.id, feature_name=f)

        records = db.query(UsageAnalytics).filter(
            UsageAnalytics.customer_id == sample_customer.id
        ).all()
        assert len(records) == 4


class TestGetCustomerUsage:
    def test_get_usage_empty(self, db, sample_customer):
        result = get_customer_usage(db=db, customer_id=sample_customer.id)
        assert result == []

    def test_get_usage_with_records(self, db, sample_customer, sample_license):
        track_usage(db=db, customer_id=sample_customer.id, feature_name="f1")
        track_usage(db=db, customer_id=sample_customer.id, feature_name="f2")

        result = get_customer_usage(db=db, customer_id=sample_customer.id)
        assert len(result) == 2

    def test_get_usage_date_filter(self, db, sample_customer, sample_license):
        track_usage(db=db, customer_id=sample_customer.id, feature_name="old_feature")

        start = datetime.now(timezone.utc) + timedelta(hours=1)
        result = get_customer_usage(db=db, customer_id=sample_customer.id, start_date=start)
        assert len(result) == 0

    def test_get_usage_only_own_records(self, db, sample_customer, sample_license):
        track_usage(db=db, customer_id=sample_customer.id, feature_name="my_feature")

        result = get_customer_usage(db=db, customer_id="other-customer")
        assert len(result) == 0


class TestGetFeatureStats:
    def test_feature_stats_empty(self, db):
        result = get_feature_stats(db=db)
        assert result == {}

    def test_feature_stats_with_data(self, db, sample_customer, sample_license):
        track_usage(db=db, customer_id=sample_customer.id, feature_name="login")
        track_usage(db=db, customer_id=sample_customer.id, feature_name="login")
        track_usage(db=db, customer_id=sample_customer.id, feature_name="export")

        result = get_feature_stats(db=db)
        assert "login" in result
        assert result["login"]["usage_count"] == 2
        assert "export" in result
        assert result["export"]["usage_count"] == 1

    def test_feature_stats_specific_feature(self, db, sample_customer, sample_license):
        track_usage(db=db, customer_id=sample_customer.id, feature_name="login")
        track_usage(db=db, customer_id=sample_customer.id, feature_name="export")

        result = get_feature_stats(db=db, feature_name="login")
        assert "login" in result
        assert "export" not in result


class TestGetAnalyticsDashboard:
    def test_dashboard_empty(self, db, sample_customer):
        result = get_analytics_dashboard(db=db, customer_id=sample_customer.id)
        assert result["total_usage"] == 0
        assert result["feature_breakdown"] == {}
        assert result["daily_usage"] == {}

    def test_dashboard_with_data(self, db, sample_customer, sample_license):
        track_usage(db=db, customer_id=sample_customer.id, feature_name="login")
        track_usage(db=db, customer_id=sample_customer.id, feature_name="login")
        track_usage(db=db, customer_id=sample_customer.id, feature_name="export")

        result = get_analytics_dashboard(db=db, customer_id=sample_customer.id)
        assert result["total_usage"] == 3
        assert result["feature_breakdown"]["login"] == 2
        assert result["feature_breakdown"]["export"] == 1

    def test_dashboard_period_days(self, db, sample_customer):
        result = get_analytics_dashboard(db=db, customer_id=sample_customer.id, days=7)
        assert result["period_days"] == 7

    def test_dashboard_has_dates(self, db, sample_customer):
        result = get_analytics_dashboard(db=db, customer_id=sample_customer.id)
        assert "start_date" in result
        assert "end_date" in result


class TestGenerateMonthlyReport:
    def test_monthly_report_empty(self, db, sample_customer):
        result = generate_monthly_report(db=db, customer_id=sample_customer.id, year=2026, month=1)
        assert result["total_usage_count"] == 0
        assert result["features_used"] == {}

    def test_monthly_report_structure(self, db, sample_customer):
        result = generate_monthly_report(db=db, customer_id=sample_customer.id, year=2026, month=5)
        assert result["customer_id"] == sample_customer.id
        assert result["year"] == 2026
        assert result["month"] == 5
        assert "generated_at" in result


class TestAdminAnalyticsOverview:
    def test_admin_overview_empty(self, db):
        result = get_admin_analytics_overview(db=db)
        assert result["total_usage"] == 0
        assert result["unique_customers"] == 0

    def test_admin_overview_with_data(self, db, sample_customer, sample_license):
        track_usage(db=db, customer_id=sample_customer.id, feature_name="login")
        track_usage(db=db, customer_id=sample_customer.id, feature_name="export")

        result = get_admin_analytics_overview(db=db)
        assert result["total_usage"] == 2
        assert result["unique_customers"] == 1
        assert "feature_stats" in result
        assert "top_features" in result
