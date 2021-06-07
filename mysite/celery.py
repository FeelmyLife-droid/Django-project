import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('balance')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()
app.conf.beat_schedule = {
    'update_balance': {
        'task': 'Company.tasks.update_balance',
        'schedule': 600,
        # 'schedule': crontab(minute=0, hour='*/1,6-23')
    },
}
