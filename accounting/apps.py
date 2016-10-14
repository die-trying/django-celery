from django.apps import AppConfig


class AccountingConfig(AppConfig):
    name = 'accounting'

    def ready(self):
        import accounting.signals   # noqa
