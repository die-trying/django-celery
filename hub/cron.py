from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'check_classes_that_will_start_soon': {
        'task': 'hub.tasks.notify_15min_to_class',
        'schedule': timedelta(minutes=1),
    },
}
