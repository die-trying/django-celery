from django.apps import AppConfig


class TimelineConfig(AppConfig):
    name = 'timeline'

    def ready(self):
        import timeline.signals  # NOQA
