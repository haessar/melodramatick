from celery import Celery

app = Celery('melodramatick')

app.config_from_object('melodramatick.celeryconfig')

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
