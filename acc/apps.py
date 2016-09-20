from django.apps import AppConfig


class AccConfig(AppConfig):
    name = 'acc'

    def ready(self):
        import acc.signals  # NOQA
