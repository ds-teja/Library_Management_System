from celery import Celery
from celery.schedules import crontab

celery = Celery(__name__,broker='redis://localhost:6379/0',backend='redis://localhost:6379/0',include=['tasks'])

CELERY_BEAT_SCHEDULE = {
    'montly_reports':{
        'task':'tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1)
    },
    'daily_reminders':{
        'task':'tasks.check_expired_books',
        'schedule': crontab(minute=1, hour=00),
    },
}

celery.conf.enable_utc = False
celery.conf.beat_schedule = CELERY_BEAT_SCHEDULE