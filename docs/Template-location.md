# How to name (and where to find) your template file

## Location

In most cases we use django-style per-app template location. Template `entry_form.html`
for app `timeline` should be located at `timeline/templates/timeline/entry_form.html` and included like

```python
from django.shortcuts import render
def my_view(request):
    return render('timeline/entry_form.html')
```

Templates to include into anothers ones are called partial templates. Place your
partial templates to the separate `_partial` subfolder of the app folder, like `timeline/templates/timeline/_partial/entry_form_err.html`
and include like this:

```
<form method = "POST">
    {% include 'timeline/_partial/entry_form_err.html' %}
</form>
```

## Naming

You should prefer django-style template naming. For example consider this generic view, located
in the app `timeline`:

```python
from django.views.generic import DetailView


class TeacherDetailView(DetailView):
    model = Teacher
```

This view will automatically find a template `timeline/teacher_detail.html`.


Here is a list of default django-style template naming:

* [ListView](https://docs.djangoproject.com/en/dev/ref/class-based-views/mixins-multiple-object/#django.views.generic.list.MultipleObjectTemplateResponseMixin) — `app/object_list.html`
* [DetailView](https://docs.djangoproject.com/en/dev/ref/class-based-views/mixins-single-object/#django.views.generic.detail.SingleObjectTemplateResponseMixin) — `app/object_detail.html`
* ModelForm — `app/object_form.html`

## Transactional email templates

We use [django-mail-templated](https://github.com/artemrizhov/django-mail-templated) for outgoing mail.

Email templates should be stored at the per-app basis, but with the same dir prefix `mail`. E.g. email template `purchase.html` for the app `market` should be located at `market/templates/mail/purcase.html` and be included like this:

```python
from mailer.owl import Owl

owl = Owl(
    to=['f@f213.in'],
    template='mail/purchase.html',
)
```

## Templatetags

Like email templates, templatetags are in single namespace too. E.g. templatetag `skype_chat` should be defined
in `skype/templatetags/skype_chat.py` and included like this
```html
{% load skype_chat %}

{% skype_chat 'test.skype' %}
```
