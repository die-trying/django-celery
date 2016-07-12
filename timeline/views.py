from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render

from timeline.models import Entry as TimelineEntry


@staff_member_required
def calendar(request, username):
    return render(request, 'calendar/user.html', context={
        'object': get_object_or_404(User, username=username)
    })


@staff_member_required
def calendar_json(request, username):
    user = get_object_or_404(User, username=username)
    entries = []
    start = request.GET.get('start', '1970-01-01')
    end = request.GET.get('end', '2100-01-01')

    for entry in get_list_or_404(TimelineEntry,
                                 start_time__range=(start, end),
                                 teacher=user
                                 ):
        entries.append(entry.as_dict())

    return JsonResponse(entries, safe=False)
