from django.contrib import admin

from crm.models import Company
from elk.admin import ModelAdmin


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    pass
