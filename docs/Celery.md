# Using Celery

We use [Celery](http://www.celeryproject.org) instead of cron for periodic tasks scheduling.

## Configuring and running on a development machine

In production environment, Celery uses Redis as storage for tasks. If you want to try some other configuration on your machine (you really shouldn't), configure `.env`:
```ini
CELERY_BROKER_URL='redis://localhost:6379'
CELERY_RESULT_BACKEND='redis://localhost:6379'
```

To run Celery on your machine, cd to the project root&virtualenv and run:
```sh
celery -A elk worker -B
```

`-B` here starts the Celery heartbeat process in the same instance.

## Defining a task

Create a file named `cron.py` in your application, and follow Celery [documentation](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#entries) to define a task.

Then, add a line to `settings.py`:
```python

CELERYBEAT_SCHEDULE = {
    'check_classes_that_will_start_soon': {
        'task': 'market.tasks.notify_15min_to_class',
        'schedule': timedelta(minutes=1),
    },

```
