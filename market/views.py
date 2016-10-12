from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from market.sortinghat import SortingHat
from teachers.models import Teacher


@login_required
def teachers(request, date, lesson_type):
    """
    Return of JSON of time slots, avaialbe for planning. The used method is
    :model:`teachers.Teacher`.find_free, filtering is done via :model:`timeline.Entry`.
    """
    date = timezone.make_aware(parse_datetime(date + ' 00:00:00'))
    teachers_with_slots = Teacher.objects.find_free(date=date, lesson_type=lesson_type)
    if not teachers_with_slots:
        raise Http404('No free teachers found')

    teachers = []
    for teacher in teachers_with_slots:
        teacher_dict = teacher.as_dict()
        teacher_dict['slots'] = teacher.free_slots.as_dict()
        teachers.append(teacher_dict)

    return JsonResponse(teachers, safe=False)


@login_required
def lessons(request, date, lesson_type):
    """
    Return a JSON of avaialble time slots for distinct date and lesson_type
    """
    date = timezone.make_aware(parse_datetime(date + ' 00:00:00'))
    lessons = Teacher.objects.find_lessons(date=date, lesson_type=lesson_type)
    if not lessons:
        raise Http404('No lessons found on this date')

    result = []
    for lesson in lessons:
        lesson_dict = lesson.as_dict()
        lesson_dict['slots'] = lesson.free_slots.as_dict()
        result.append(lesson_dict)

    return JsonResponse(result, safe=False)


@login_required
def step1(request):
    return render(request, 'market/schedule_popup/schedule_popup.html')


@login_required
def step2(request, teacher, type_id, date, time):
    hat = SortingHat(
        customer=request.user.crm,
        teacher=get_object_or_404(Teacher, pk=teacher),
        lesson_type=type_id,
        date=date,
        time=time,
    )

    hat.do_the_thing()  # do the actual scheduling

    if 'check' in request.GET.keys():
        return JsonResponse({
            'result': hat.result,
            'error': hat.err,
            'text': hat.msg,
        })

    if not hat.result:
        raise Http404('%s: %s' % (hat.err, hat.msg))

    hat.c.save()  # save a hat-generated class
    return redirect('/')  # TODO: a page with success story


@login_required
def cancel_popup(request, class_id):
    if not request.user.crm.can_cancel_classes():
        return render(request, 'market/cancel_popup/sorry.html')

    return render(request, 'market/cancel_popup/index.html', context={
        'object': get_object_or_404(request.user.crm.classes, pk=class_id, is_scheduled=True),
    })


@login_required
def cancel(request, class_id):
    c = get_object_or_404(request.user.crm.classes, pk=class_id)
    if not request.user.crm.can_cancel_classes():
        return JsonResponse({'result': False}, safe=False)

    if not c.can_be_unscheduled():
        return JsonResponse({'result': False}, safe=False)

    c.cancel(src='customer')
    c.save()
    return JsonResponse({'result': True}, safe=False)
