from django.apps import AppConfig


class MailerConfig(AppConfig):
    name = 'mailer'

    def ready(self):
        import mailer.signals  # NOQA
