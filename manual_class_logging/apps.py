from django.apps import AppConfig


class ManualClassLoggingConfig(AppConfig):
    name = 'manual_class_logging'

    def ready(self):
        import manual_class_logging.signals  # NOQA
