from django.contrib import admin

# Register your models here.
from student_card.models import CardInfo


class CardInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'photo', 'emergency_contact_name', 'emergency_phone_number', 'organ_donor', 'created_at')
    list_filter = ('organ_donor',)
    search_fields = ('id',)


admin.site.register(CardInfo, CardInfoAdmin)
