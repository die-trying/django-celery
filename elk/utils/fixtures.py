"""
Tiny fixture helper to generate `mixer<https://github.com/klen/mixer>`_-based
fixtures with correct relations.

Every new call returnes a new fixture.
"""
from mixer.backend.django import mixer


def test_customer():
    user = mixer.blend('auth.user')
    return mixer.blend('crm.customer', user=user)


def test_teacher():
    customer = test_customer()
    return mixer.blend('teachers.teacher', user=customer.user)  # second level relations — that is wy i've created this helper
