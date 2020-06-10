from django.contrib import admin

from documents.models import Category, Document


class CategoryAdmin(admin.ModelAdmin):
    """Category Model Admin"""
    list_display = ('name', 'description', 'created_at', 'updated_at', 'disabled')
    search_fields = ('name',)


class DocumentAdmin(admin.ModelAdmin):
    """Document Model Admin"""
    list_display = ('id', 'file', 'category', 'user', 'comment', 'created_at')
    search_fields = ('file',)
    list_filter = ('category__name', 'user__username')


# Register admin
admin.site.register(Category, CategoryAdmin)
admin.site.register(Document, DocumentAdmin)
