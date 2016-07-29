from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, JsonResponse
from django.shortcuts import get_list_or_404

from teachers.models import Teacher


@staff_member_required
def available_lessons(request, username):
    lesson_type = request.GET.get('lesson_type')

    # We don't limit lessons to users. If you need it sometimes, fill free
    # to filter your query
    Model = ContentType.objects.get(app_label='lessons', pk=lesson_type).model_class()

    lessons = []
    for lesson in get_list_or_404(Model):
        lessons.append(lesson.as_dict())

    return JsonResponse(lessons, safe=False)


@login_required
def slots_by_type(request, date, lesson_type):
    """
    Return a JSON of avaialble time slots for distinct date and lesson_type

    Further you may add support for filtering via request_filters, like at
    :view:`teachers.slots_by_teacher`.
    """
    lessons = Teacher.objects.find_lessons(date=date, lesson_type=lesson_type)
    if not lessons:
        raise Http404('No lessons found on this date')

    result = []
    for lesson in lessons:
        lesson_dict = lesson.as_dict()
        lesson_dict['slots'] = lesson.free_slots.as_dict()
        result.append(lesson_dict)

    return JsonResponse(result, safe=False)
