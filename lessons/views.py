from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_list_or_404


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
