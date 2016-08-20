from django.dispatch import Signal

new_user_registered = Signal(providing_args=['user', 'whom_to_notify'])  # class is just scheduled
