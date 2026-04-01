# crowd_safety/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowd_safety.settings')

app = Celery('crowd_safety')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def fetch_global_alerts_task(self):
    from alerts.services import RealTimeAlertManager
    manager = RealTimeAlertManager()
    return manager.process_and_save_alerts()

# Schedule to run every 5 minutes
app.conf.beat_schedule = {
    'fetch-global-alerts': {
        'task': 'crowd_safety.celery.fetch_global_alerts_task',
        'schedule': crontab(minute='*/5'),
    },
}