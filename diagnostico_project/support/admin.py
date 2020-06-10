from django.contrib import admin

from support.models import Comment, Task, Ticket


class CommentInLine(admin.TabularInline):
    """Comment In Line"""
    model = Comment


class TaskAdmin(admin.ModelAdmin):
    """Task Admin"""
    list_display = ('title', 'created_at', 'updated_at', 'disabled')
    search_fields = ('title',)


class TicketAdmin(admin.ModelAdmin):
    """Ticket Admin"""
    list_display = ('user', 'task', 'status', 'created_at', 'updated_at', 'disabled')
    search_fields = ('user', 'task', 'status')
    inlines = [
        CommentInLine
    ]


class CommentAdmin(admin.ModelAdmin):
    """Comment Admin"""
    list_display = ('user', 'ticket', 'text', 'created_at')
    search_fields = ('user', 'ticket')


# Register models
admin.site.register(Task, TaskAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Comment, CommentAdmin)