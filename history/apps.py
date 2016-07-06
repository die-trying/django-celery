from django.apps import AppConfig


class HistoryConfig(AppConfig):
    name = 'history'

    def ready(self):
        import history.signals
