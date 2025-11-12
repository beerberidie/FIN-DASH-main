"""Scheduler service for automated tasks in FIN-DASH."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from services.recurring_service import recurring_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled tasks."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False

    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        # Schedule recurring transaction processing
        # Run daily at 00:01 (1 minute past midnight)
        self.scheduler.add_job(
            func=self.process_recurring_transactions,
            trigger=CronTrigger(hour=0, minute=1),
            id="process_recurring_transactions",
            name="Process Recurring Transactions",
            replace_existing=True,
        )

        # Also run on startup (after a short delay)
        self.scheduler.add_job(
            func=self.process_recurring_transactions,
            trigger="date",
            run_date=datetime.now(),
            id="process_recurring_transactions_startup",
            name="Process Recurring Transactions (Startup)",
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("Scheduler started successfully")

    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")

    def process_recurring_transactions(self):
        """Process all due recurring transactions."""
        try:
            logger.info("Processing recurring transactions...")
            generated = recurring_service.process_due_transactions()
            logger.info(f"Generated {len(generated)} transactions from recurring rules")
            return generated
        except Exception as e:
            logger.error(f"Error processing recurring transactions: {str(e)}")
            return []

    def get_jobs(self):
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()


# Singleton instance
scheduler_service = SchedulerService()
