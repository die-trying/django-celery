from django.apps import AppConfig


class ExtEventsConfig(AppConfig):
    name = 'extevents'

    def ready(self):
        import extevents.signals  # NOQA
