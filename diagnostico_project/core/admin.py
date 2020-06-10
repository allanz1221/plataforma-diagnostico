from django.contrib import admin

from core.models import FaqItem


class FaqItemAdmin(admin.ModelAdmin):
    """Faq Item Admin"""
    list_display = ('question', 'answer', 'created_at', 'updated_at')


admin.site.register(FaqItem, FaqItemAdmin)
