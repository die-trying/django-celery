"""
Abstract admin classes. All your ModelAdmins should be subclasses from this Modeladmin
"""
from django.contrib import admin

from .model_admin import *  # noqa


admin.site.disable_action('delete_selected')  # disable delete selected action site-wide
