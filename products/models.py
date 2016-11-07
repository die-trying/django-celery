from datetime import timedelta

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField

from lessons.models import HappyHour, LessonWithNative, MasterClass, OrdinaryLesson, PairedLesson


class Product(models.Model):
    """
    Base class for every product, that user can buy
    """
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )

    active = models.IntegerField(default=1, choices=ENABLED)
    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    name = models.CharField(max_length=140)
    internal_name = models.CharField(max_length=140)

    duration = models.DurationField(default=timedelta(days=7 * 6))

    def __str__(self):
        return self.internal_name

    def get_tier(self, country):
        """
        Get pricing tier for distinct country
        """
        return Tier.objects.get_for_product(self, country)

    def ship(self, customer):
        """
        Abstract method for shipping a product to customer.

        Shipping should be simple creating an instance of subclassed :model:`market.ProductContainer`
        """
        raise NotImplemented('Please implement in subclass')

    def get_success_template_name(self):
        raise NotImplemented('Please implement in subclass')

    class Meta:
        abstract = True


class SingleLessonProduct(Product):
    """
    Product for purchasing a single lesson of any type.

    Please create this products by migrations, not through admin.
    """
    lesson_type = models.ForeignKey(ContentType, limit_choices_to={'app_label': 'lessons'})

    def ship(self, customer):
        Class = apps.get_model('market.Class')
        c = Class(
            customer=customer,
            lesson_type=self.lesson_type,
        )
        c.save()

    def get_success_template_name(self):
        return 'payments/single_lesson_success.html'

    class Meta:
        verbose_name = 'Single lesson'


class ProductWithLessons(Product):
    """
    Base class for products that contain multiple lessons.

    Please don't use admin for managing lessons of particular product —
    use the migrations. Example migration you can find ad products/migrations/0002_simplesubscription.py
    """

    def ship(self, customer):
        Subscription = apps.get_model('market.Subscription')

        s = Subscription(
            customer=customer,
            product=self,
        )

        s.save()

    def get_success_template_name(self):
        return 'payments/subscription_success.html'

    def lessons(self):
        """
        Get all lesson attributes of a subscription
        """
        for i in self.LESSONS:
            yield getattr(self, i)

    def lesson_types(self):
        """
        Get ContentTypes of lessons, that are included in the product
        """
        for bundled_lesson in self.lessons():
            yield bundled_lesson.model.get_contenttype()

    def classes_by_lesson_type(self, lesson_type):
        """
        Get all lessons in subscription by contenttype
        """
        for bundled_lesson in self.lessons():
            if bundled_lesson.model.get_contenttype() == lesson_type:
                return bundled_lesson.all()

    class Meta:
        abstract = True


class Product1(ProductWithLessons):
    """
    Stores information about subscriptions of the first type.
    """
    LESSONS = (
        'ordinary_lessons',
        'lessons_with_native',
        'paired_lessons',
        'happy_hours',
        'master_classes'
    )

    ordinary_lessons = models.ManyToManyField(OrdinaryLesson, limit_choices_to={'active': 1})
    lessons_with_native = models.ManyToManyField(LessonWithNative, limit_choices_to={'active': 1})
    paired_lessons = models.ManyToManyField(PairedLesson, limit_choices_to={'active': 1})
    happy_hours = models.ManyToManyField(HappyHour, limit_choices_to={'active': 1})
    master_classes = models.ManyToManyField(MasterClass, limit_choices_to={'active': 1})

    class Meta:
        verbose_name = "Subscription type: first subscription"
        verbose_name_plural = "Subscriptions of the first type"


class SimpleSubscription(ProductWithLessons):
    """
    Simple subscription for beginners
    """
    LESSONS = (
        'ordinary_lessons',
        'lessons_with_native',
        'paired_lessons',
    )
    ordinary_lessons = models.ManyToManyField(OrdinaryLesson, limit_choices_to={'active': 1})
    paired_lessons = models.ManyToManyField(PairedLesson, limit_choices_to={'active': 1})
    lessons_with_native = models.ManyToManyField(LessonWithNative, limit_choices_to={'active': 1})

    class Meta:
        verbose_name = "Subscription type: beginners subscription"
        verbose_name_plural = "Beginner subscriptions"


class TierManager(models.Manager):
    def get_for_product(self, product, country):
        """
        Get payment tier for product and country. If country is not found, returns a default tier
        """
        normal_tier = self.get_queryset().filter(
            product_id=product.pk,
            product_type=ContentType.objects.get_for_model(product),
            country=country,
        )
        if normal_tier.count():
            return normal_tier.first()

        default_tier = self.get_queryset().filter(
            product_id=product.pk,
            product_type=ContentType.objects.get_for_model(product),
            is_default=True,
        )
        return default_tier.first()


class Tier(models.Model):
    """
    Product tier is a product price for single country.

    Currently single tier for multiple countries is not supported because
    django country field does not support m2m.

    You should create a default tier for every product, which objects.get_for_product()
    will return when it can't find a country.
    """
    objects = TierManager()

    country = CountryField(null=True)
    is_default = models.BooleanField(default=False)
    name = models.CharField('Tier name', max_length=140)

    product_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'app_label': 'products'})
    product_id = models.PositiveIntegerField(default=1)
    product = GenericForeignKey('product_type', 'product_id')

    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    def __str__(self):
        product_type = str(self.product_type).replace('Subscription type: ', '')
        if self.is_default:
            return 'Default tier for %s' % product_type
        else:
            return 'Tier for %s in %s' % (product_type, self.country.name)

    class Meta:
        unique_together = ('country', 'product_id', 'product_type', 'is_default')
