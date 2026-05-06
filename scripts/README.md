# Email Queue Processing Scripts

This directory contains scripts for processing the email queue and sending scheduled emails.

## Scripts

### 1. process_emails.py

Processes pending emails in the email queue and sends them via SMTP.

**Usage:**
```bash
python scripts/process_emails.py
```

**Cron Setup (every 1 minute):**
```bash
* * * * * cd /path/to/license-server && python scripts/process_emails.py >> logs/email_queue.log 2>&1
```

**What it does:**
- Fetches pending emails from the email_queue table
- Sends emails via SMTP server
- Updates email status (sent/failed)
- Implements retry logic (up to 3 attempts)
- Logs all operations

### 2. send_trial_reminders.py

Sends trial reminder emails to customers whose trial is ending soon.

**Usage:**
```bash
python scripts/send_trial_reminders.py
```

**Cron Setup (daily at 9 AM):**
```bash
0 9 * * * cd /path/to/license-server && python scripts/send_trial_reminders.py >> logs/trial_reminders.log 2>&1
```

**What it does:**
- Checks all active trial licenses
- Identifies trials ending in 3 days or 1 day
- Queues reminder emails for eligible customers
- Logs all operations

### 3. send_payment_due_reminders.py

Sends payment due reminder emails to customers whose subscriptions are expiring soon.

**Usage:**
```bash
python scripts/send_payment_due_reminders.py
```

**Cron Setup (daily at 10 AM):**
```bash
0 10 * * * cd /path/to/license-server && python scripts/send_payment_due_reminders.py >> logs/payment_due_reminders.log 2>&1
```

**What it does:**
- Checks all active paid licenses (basic/premium)
- Identifies subscriptions expiring in 7 days or 3 days
- Queues payment due reminder emails for eligible customers
- Logs all operations

### 4. monitor_failed_emails.py

Monitors the email queue for failed emails and generates alerts.

**Usage:**
```bash
python scripts/monitor_failed_emails.py
```

**Cron Setup (every hour):**
```bash
0 * * * * cd /path/to/license-server && python scripts/monitor_failed_emails.py >> logs/email_monitoring.log 2>&1
```

**What it does:**
- Counts failed emails in the last hour
- Identifies emails with high retry counts
- Generates alerts if failure threshold exceeded
- Provides summary statistics

## APScheduler Integration (Alternative to Cron)

Instead of using cron jobs, you can use the built-in APScheduler integration in `app/main.py`.

**Advantages:**
- No need to configure cron jobs
- Runs within the FastAPI application
- Easier to manage and monitor
- Works on Windows without additional setup

**Scheduled Jobs:**
1. **Email Queue Processing**: Runs every 1 minute
2. **Trial Reminders**: Runs daily at 9 AM
3. **Payment Due Reminders**: Runs daily at 10 AM

**Configuration:**

The scheduler is automatically started when the FastAPI application starts. You can modify the schedule in `app/main.py`:

```python
# Email queue processing (every 1 minute)
scheduler.add_job(
    process_email_queue_job,
    trigger=IntervalTrigger(minutes=1),
    id='process_email_queue',
    name='Process Email Queue',
    replace_existing=True
)

# Trial reminders (daily at 9 AM)
scheduler.add_job(
    send_trial_reminders_job,
    trigger=CronTrigger(hour=9, minute=0),
    id='send_trial_reminders',
    name='Send Trial Reminders',
    replace_existing=True
)
```

## Logging

All scripts log to stdout. When running via cron, redirect output to log files:

```bash
# Create logs directory if it doesn't exist
mkdir -p logs

# Run with logging
python scripts/process_emails.py >> logs/email_queue.log 2>&1
```

## Environment Variables

Ensure the following environment variables are set in `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@salarypay.com
SMTP_USE_TLS=True
```

## Monitoring and Alerting

### Email Delivery Monitoring

The `monitor_failed_emails.py` script provides basic monitoring:

- Tracks failed emails in the last hour
- Alerts if more than 10 emails fail per hour
- Identifies emails on their last retry attempt

### Production Recommendations

For production environments, consider:

1. **External Monitoring**: Use services like Datadog, New Relic, or Sentry
2. **Email Alerts**: Configure alerts to notify admins of failures
3. **Dashboard**: Create a monitoring dashboard for email queue metrics
4. **Log Aggregation**: Use ELK stack or similar for centralized logging

## Troubleshooting

### Emails Not Sending

1. Check SMTP configuration in `.env`
2. Verify SMTP credentials are correct
3. Check firewall/network settings
4. Review logs for error messages
5. Test SMTP connection manually

### High Failure Rate

1. Check SMTP server status
2. Verify email format and content
3. Check for rate limiting
4. Review error messages in email_queue table

### Scheduler Not Running

1. Verify FastAPI application is running
2. Check application logs for scheduler startup messages
3. Ensure APScheduler is installed: `pip install apscheduler`

## Testing

### Test Email Queue Processing

```bash
# Add test email to queue
python -c "
from app.database import SessionLocal
from app.services.email import queue_email

db = SessionLocal()
queue_email(
    db=db,
    to_email='test@example.com',
    subject='Test Email',
    body_html='<p>This is a test</p>',
    body_text='This is a test'
)
db.close()
print('Test email queued')
"

# Process queue
python scripts/process_emails.py
```

### Test Trial Reminders

```bash
# Run trial reminder check
python scripts/send_trial_reminders.py
```

### Test Monitoring

```bash
# Run monitoring script
python scripts/monitor_failed_emails.py
```

## Performance

- Email queue processing handles up to 100 emails per batch
- Processing time: ~1-2 seconds per email
- Recommended frequency: Every 1 minute for queue processing
- Trial reminders: Once daily is sufficient

## Security

- Never commit `.env` file with real credentials
- Use app-specific passwords for Gmail
- Restrict script execution permissions
- Monitor for suspicious email activity
- Implement rate limiting if needed
