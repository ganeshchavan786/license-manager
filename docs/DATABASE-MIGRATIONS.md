# Database Migrations Guide

## Overview

This document explains how to manage database migrations for the SalaryPay License Server using Alembic.

## Prerequisites

- Python 3.10+
- Alembic 1.13.1+ installed
- SQLite database (license.db)

## Migration Files

All migration files are located in `alembic/versions/`:

1. **001_add_usage_analytics_table.py** - Usage analytics tracking
2. **002_add_promo_code_tables.py** - Promo codes and usage tracking
3. **003_add_email_queue_table.py** - Email queue for async sending
4. **004_add_invoices_table.py** - GST-compliant invoices
5. **005_add_team_members_table.py** - Team management with roles

## Running Migrations

### Apply All Pending Migrations

```bash
# Upgrade to latest version
python -m alembic upgrade head
```

### Apply Specific Migration

```bash
# Upgrade to specific revision
python -m alembic upgrade 003
```

### Check Current Version

```bash
# Show current migration version
python -m alembic current
```

### View Migration History

```bash
# Show all migrations
python -m alembic history
```

## Rolling Back Migrations

### Rollback One Migration

```bash
# Downgrade by 1 version
python -m alembic downgrade -1
```

### Rollback to Specific Version

```bash
# Downgrade to specific revision
python -m alembic downgrade 002
```

### Rollback All Migrations

```bash
# Downgrade to base (empty database)
python -m alembic downgrade base
```

## Creating New Migrations

### Auto-generate Migration

```bash
# Generate migration from model changes
python -m alembic revision --autogenerate -m "description"
```

### Manual Migration

```bash
# Create empty migration file
python -m alembic revision -m "description"
```

## Production Deployment

### Step 1: Backup Database

```bash
# Windows
copy license.db license.db.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%

# Linux/Mac
cp license.db license.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Step 2: Test Migrations on Staging

```bash
# Copy production database to staging
# Run migrations on staging first
python -m alembic upgrade head

# Verify tables created
python -c "from app.database import engine; import sqlalchemy; print(sqlalchemy.inspect(engine).get_table_names())"
```

### Step 3: Apply to Production

```bash
# During low-traffic window
python -m alembic upgrade head
```

### Step 4: Verify

```bash
# Check current version
python -m alembic current

# Verify application works
curl http://localhost:8661/health
```

## Rollback Plan

If migrations fail in production:

```bash
# Step 1: Rollback migrations
python -m alembic downgrade -1

# Step 2: Restore from backup if needed
# Windows
copy license.db.backup.YYYYMMDD license.db

# Linux/Mac
cp license.db.backup.YYYYMMDD_HHMMSS license.db

# Step 3: Restart application
systemctl restart salarypay-license
```

## Troubleshooting

### Error: "Can't locate revision identified by 'XXX'"

**Solution**: Check alembic_version table

```bash
python -c "from app.database import engine; import pandas as pd; print(pd.read_sql('SELECT * FROM alembic_version', engine))"
```

### Error: "Table already exists"

**Solution**: Mark migration as applied without running

```bash
python -m alembic stamp head
```

### Error: "UNIQUE constraint failed"

**Solution**: Check for duplicate data before migration

```bash
# Check for duplicates
python -c "from app.database import engine; import pandas as pd; print(pd.read_sql('SELECT code, COUNT(*) FROM promo_codes GROUP BY code HAVING COUNT(*) > 1', engine))"
```

## Migration Safety Checklist

Before running migrations in production:

- [ ] Database backup created
- [ ] Migrations tested on staging
- [ ] Rollback plan documented
- [ ] Low-traffic window scheduled
- [ ] Team notified
- [ ] Monitoring alerts configured
- [ ] Rollback tested on staging

## New Tables Created

### usage_analytics
- Tracks feature usage per customer
- Indexes on customer_id, feature_name, created_at

### promo_codes
- Stores discount codes
- Unique index on code
- Indexes on is_active, expiry_date

### promo_code_usage
- Tracks promo code usage
- Indexes on promo_code_id, customer_id, payment_id

### email_queue
- Queues emails for async sending
- Indexes on status, scheduled_at, to_email

### invoices
- Stores GST-compliant invoices
- Unique index on invoice_number
- Indexes on customer_id, payment_id

### team_members
- Manages team members per license
- Indexes on license_id, email, invitation_token

## Backward Compatibility

All migrations are designed to be backward compatible:

- New tables only (no modifications to existing tables)
- All new columns have default values
- Foreign keys use SET NULL on delete
- Existing APIs continue working unchanged

## Support

For migration issues:
- Check logs: `tail -f /var/log/salarypay-license.err.log`
- Review migration file: `cat alembic/versions/XXX_description.py`
- Contact: support@salarypay.com

---

**Last Updated**: May 5, 2026  
**Version**: 1.0.0
