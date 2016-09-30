from django.apps import AppConfig


class CRMConfig(AppConfig):
    name = 'crm'
    verbose_name = 'CRM'

    def ready(self):
        import crm.signals  # NOQA
