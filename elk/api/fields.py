from django_markdown.utils import markdown
from rest_framework import serializers


class MarkdownField(serializers.Field):
    """
    Return HTML rendered from Django-markdown (https://github.com/sv0/django-markdown-app)
    """
    def to_representation(self, obj):
        return markdown(obj)
