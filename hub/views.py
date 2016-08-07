from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from moneyed import Money

from hub.models import Class, Subscription
from hub.sortinghat import SortingHat
from lessons.models import OrdinaryLesson
from products.models import Product1
from teachers.models import Teacher


@login_required
def single(request):
    c = Class(
        customer=request.user.crm,
        lesson=OrdinaryLesson.get_default(),
        buy_price=Money(10, 'USD'),
    )
    c.request = request
    c.save()
    return redirect('/')


@login_required
def subscription(request):
    s = Subscription(
        customer=request.user.crm,
        product=Product1.objects.get(pk=1),
        buy_price=Money(150, 'USD')
    )
    s.request = request
    s.save()
    return redirect('/')


@login_required
def teachers(request, date, lesson_type):
    """
    Return of JSON of time slots, avaialbe for planning. The used method is
    :model:`teachers.Teacher`.find_free, filtering is done via :model:`timeline.Entry`.
    """
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
    return render(request, 'hub/schedule_popup/schedule_popup.html')


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
        return Http404('%s: %s' % (hat.err, hat.msg))

    hat.c.save()  # save a hat-generated class
    return redirect('/')  # TODO: a page with success story


@login_required
def cancel_popup(request, class_id):
    if not request.user.crm.can_cancel_classes():
        return render(request, 'hub/cancel_popup/sorry.html')

    return render(request, 'hub/cancel_popup/index.html', context={
        'object': get_object_or_404(request.user.crm.classes, pk=class_id, is_scheduled=True),
    })


@login_required
def cancel(request, class_id):
    c = get_object_or_404(request.user.crm.classes, pk=class_id)
    if not request.user.crm.can_cancel_classes():
        return JsonResponse({'result': False}, safe=False)

    c.unschedule(src='customer')
    c.save()
    return JsonResponse({'result': True}, safe=False)
