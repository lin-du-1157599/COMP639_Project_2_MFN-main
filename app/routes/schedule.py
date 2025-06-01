from app import app
from datetime import datetime, timedelta
from flask_apscheduler import APScheduler
from app.config import constants
from app.db import db
from pytz import timezone

scheduler = APScheduler()

def notify_expiring_subscriptions():
    print('$$$$$$ Excute notify_expiring_subscriptions')
    with app.app_context():
        with db.get_cursor() as cursor:
            today = datetime.utcnow().date()
            one_week_later = today + timedelta(days=7)

            # Find users whose subscriptions will expire within 7 days.
            cursor.execute("""
                SELECT user_id, subscription_end_date FROM users
                WHERE subscription_end_date BETWEEN %s AND %s
            """, (today, one_week_later))
            users = cursor.fetchall()

            for user in users:
                user_id = user[constants.USER_ID]
                subscription_end_date = user[constants.USER_SUBSCRIPTION_END_DATE]
                title = 'Don’t Miss Out! Your Subscription Ends Soon'
                content = f"Your subscription will expire on {subscription_end_date}. Please renew it in time."

                # The reminder will be sent only once."
                cursor.execute("""
                    SELECT COUNT(*) as count FROM announcements
                    WHERE recipient_id = %s
                    AND subscription_end_date = %s
                    AND title = %s
                """, (user_id, subscription_end_date, title))
                already_sent = cursor.fetchone()['count']
                if already_sent == 0:
                    print('######## Schedule insert announcements')
                    cursor.execute("""
                        INSERT INTO announcements (title, content, recipient_id, subscription_end_date)
                        VALUES(%s, %s, %s, %s)
                    """, (title, content, user_id, subscription_end_date))

def init_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()
    # Set to run every day at 12:05 AM New Zealand time
    nz_timezone = timezone('Pacific/Auckland')
    scheduler.add_job(
        id='check_subscriptions',
        func=notify_expiring_subscriptions,
        trigger='cron',
        hour=0,
        minute=5,
        timezone=nz_timezone
    )

# def init_scheduler(app):
#     scheduler.init_app(app)
#     scheduler.start()
#     # Run every 1 minute
#     scheduler.add_job(
#         id='notify_expiring_subscriptions',
#         func=notify_expiring_subscriptions,
#         trigger='interval',
#         minutes=1
#     )

