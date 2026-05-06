"""
Unit Tests - Email Service
Task 24.3: Write unit tests for email service (80% coverage)
"""
import pytest
from app.services.email import queue_email
from app.models import EmailQueue


class TestQueueEmail:
    def test_queue_email_success(self, db):
        result = queue_email(
            db=db,
            to_email="test@example.com",
            subject="Test Subject",
            body_html="<p>Test</p>",
            body_text="Test"
        )
        assert result is not None
        assert result.to_email == "test@example.com"
        assert result.subject == "Test Subject"
        assert result.status == "pending"

    def test_queue_email_default_status(self, db):
        result = queue_email(
            db=db,
            to_email="user@test.com",
            subject="Hello",
            body_html="<p>Hello</p>"
        )
        assert result.status == "pending"
        assert result.retry_count == 0

    def test_queue_multiple_emails(self, db):
        for i in range(3):
            queue_email(
                db=db,
                to_email=f"user{i}@test.com",
                subject=f"Email {i}",
                body_html=f"<p>Email {i}</p>"
            )
        count = db.query(EmailQueue).count()
        assert count == 3

    def test_queue_email_stored_in_db(self, db):
        queue_email(
            db=db,
            to_email="stored@test.com",
            subject="Stored",
            body_html="<p>Stored</p>"
        )
        record = db.query(EmailQueue).filter(
            EmailQueue.to_email == "stored@test.com"
        ).first()
        assert record is not None
        assert record.subject == "Stored"


class TestEmailQueueEndpoints:
    def test_get_email_queue_admin(self, client, admin_token):
        response = client.get(
            "/api/email/admin/queue",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
