from django.dispatch import Signal, receiver

from mailer.owl import Owl

trial_lesson_added = Signal()


@receiver(trial_lesson_added, dispatch_uid='notify_new_customer_about_trial_lesson')
def notify_new_customer_about_trial_lesson(sender, **kwargs):
    owl = Owl(
        template='mail/trial_lesson_added.html',
        ctx={
            'c': sender,
        },
        to=[sender.user.email],
        timezone=sender.timezone,
    )
    owl.send()
