from mail_templated import EmailMessage

MAIL_FROM = 'ELK Academy <notifications@elk.academy>'


class Owl():
    """
    Simple templating email wrapper. By now it uses  https://github.com/f213/django-mail-templated

    For usage examples please see tests.
    """
    def __init__(self, template, ctx, to=[]):
        self.template = template
        self.ctx = ctx
        self.to = to

    @property
    def EmailMessage(self):
        return EmailMessage(
            self.template,
            self.ctx,
            MAIL_FROM,
            self.to
        )
