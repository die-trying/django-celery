from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext as _

from hub.exceptions import CannotBeScheduled


class SortingHat():
    """
    SortingHat is a class for scheduling a lesson. All required parameters should
    be passed to the constructor, like:

        from class.scheduler import SortingHat

        hat = SortingHat(
            customer=request.user.crm
            lesson_type=lesson_type,
            teacher=get_object_or_404('teachers.Teacher', teacher)
            date='2016-05-28',
            time='13:37',
        )

        if not hat.do_the_thing():
            # here goes your error logic
            return JsonResponse({
                err = {
                    'code': hat.err,
                    'message': hat.msg
                }
            })
        else:
            hat.c.save()    # actualy schedule a user-bought class, found by the hat.
                            # 'c' here is an instance of :model:`hub.Class`

    This class is supposed to be a god-object for further class scheduling logic,
    so it should be covered by unit-tests (not fucntional, but UNIT) for 100%.
    """
    result = True   # Boolean, defining if all is correct
    err = 'E_NONE'  # error code (see the code-dictionary below)
    msg = ''        # error message
    c = None        # found class
    entry = None    # timeline entry for planning
    errs = {
        'E_NONE': '',
        'E_CLASS_NOT_FOUND': _("You don't have available lessons"),
        'E_ENTRY_NOT_FOUND': _("Your choice is not found in the curriculum"),
        'E_CANT_SCHEDULE': _("Your choice does not fit teachers timeline"),
        'E_UNKNOWN': "Unknown scheduling error"
    }

    def do_the_thing(self):
        """
        Do all the planning magic:
            1) Find a class
            2) Find a timeline entry if user's lesson require it
            3) Schedule it
        """
        for staff in self.find_a_class, self.find_an_entry, self.schedule_a_class:
            staff()
            if not self.result:
                return False
        return True

    def __init__(self, customer, lesson_type, teacher, date, time):
        self.customer = customer
        self.lesson_type = ContentType.objects.get(app_label='lessons', pk=lesson_type)
        self.teacher = teacher
        self.date = timezone.make_aware(parse_datetime(date + ' ' + time))

    def __set_err(self, err='E_NONE', msg=None):
        """
        Set error code
        """
        if err not in self.errs.keys():
            err = 'E_UNKNOWN'

        if msg is None:
            msg = self.errs.get(err)

        self.err = err
        self.msg = msg

        if err == 'E_NONE':
            self.result = True
        else:
            self.result = False

    def __get_class(self):
        """
        Find a bought class for defined customer with defined lesson_type, that
        has not yet been scheduled.
        """
        Class = apps.get_model('hub.Class')
        return Class.objects \
            .filter(customer=self.customer) \
            .filter(lesson_type=self.lesson_type) \
            .filter(is_scheduled=False) \
            .order_by('subscription_id', 'buy_date') \
            .first()

    def __get_entry(self):
        """
        Find a free timeline entry of selected teacher, that can accept defined
        lesson_type and starts just when user wants it.
        """
        TimelineEntry = apps.get_model('timeline.entry')
        return TimelineEntry.objects \
            .filter(taken_slots__lt=F('slots')) \
            .filter(teacher=self.teacher) \
            .filter(lesson_type=self.lesson_type) \
            .filter(start=self.date) \
            .first()

    def find_a_class(self):
        """
        Find a bought class. When no appropriate bought class found, it means that
        the user can't schedule his choice.
        """
        c = self.__get_class()
        if c is not None:
            self.c = c
            self.__set_err('E_NONE')
            return
        self.__set_err('E_CLASS_NOT_FOUND')

        """ Create a more verbose error message """
        Lesson = self.lesson_type.model_class()
        msg = "You don't have available " + Lesson._meta.verbose_name_plural.lower()
        self.__set_err('E_CLASS_NOT_FOUND', msg)

    def find_an_entry(self):
        """
        Find a timeline entry. If no timeline entry is required for user's lesson,
        this method simply changes nothing and exits.
        """
        Lesson = self.lesson_type.model_class()

        if not Lesson.timeline_entry_required():
            return
        entry = self.__get_entry()
        if entry is not None:
            self.entry = entry
            self.__set_err('E_NONE')
            return
        self.__set_err('E_ENTRY_NOT_FOUND')

    def schedule_a_class(self):
        """
        Actualy assign a timeline entry to the class. If there is not entry, the
        class will create it by itself by the :model:`hub.Class`.schedule() method.

        The situation where there is not a timeline entry before calling this method
        is usual: some lessons, like OrdinaryLesson, do not require it.
        """
        try:
            if self.entry:  # if the entry was created by find_an_entry, that the lesson needs it
                self.c.assign_entry(self.entry)
            else:  # otherwise — schedule it without an entry
                self.c.schedule(
                    teacher=self.teacher,
                    date=self.date
                )
        except CannotBeScheduled:
            """
            Should not be thrown in normal circumstances. When you see this error,
            check the method :model:`hub.class`.can_be_scheduled() — there are all
            the reasons, that throw this excpetions. You can comment them one by one
            any find the reason.
            """
            self.__set_err('E_CANT_SCHEDULE')
            return

        self.__set_err('E_NONE')
