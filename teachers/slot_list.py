from collections import UserList

from django.template.defaultfilters import time
from django.utils import timezone


class SlotList(UserList):
    def as_dict(self):
        return [
            {
                'server': time(timezone.localtime(i), 'H:i'),
                'user': time(timezone.localtime(i), 'TIME_FORMAT')
            } for i in sorted(self.data)]
