from django.contrib import admin
from .models import VisitRequest

@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'national_id', 'inmate_id', 'phone', 'relation', 'status', 'created_at')
    list_filter = ('status', 'relation', 'created_at')
    search_fields = ('full_name', 'national_id', 'inmate_id', 'phone')
