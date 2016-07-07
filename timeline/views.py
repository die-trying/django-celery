from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_list_or_404, get_object_or_404
from jsonview.decorators import json_view

from timeline.models import Entry as TimelineEntry


@login_required
def calendar(request, username):
    pass


@json_view
def calendar_json(request, username):
    user = get_object_or_404(User, username=username)
    entries = []
    for entry in get_list_or_404(TimelineEntry, teacher=user):
        entries.append(entry.as_dict())

    return entries
