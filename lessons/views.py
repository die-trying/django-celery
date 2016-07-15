from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404


@staff_member_required
def available_lessons_json(request, username):
    lesson_id = request.GET.get('lesson_id')

    # We don't limit lessons to you users. If you need it sometimes, fill free
    # to filter your query
    user = get_object_or_404(User, username=username)  # NOQA
    Model = ContentType.objects.get(app_label='lessons', pk=lesson_id).model_class()

    lessons = []
    for lesson in get_list_or_404(Model):
        lessons.append(lesson.as_dict())

    return JsonResponse(lessons, safe=False)
