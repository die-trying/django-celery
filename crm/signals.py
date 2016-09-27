from django.dispatch import Signal, receiver

trial_lesson_added = Signal()


@receiver(trial_lesson_added, dispatch_uid='notify_new_customer_about_trial_lesson')
def notify_new_customer_about_trial_lesson(sender, **kwargs):
    pass
