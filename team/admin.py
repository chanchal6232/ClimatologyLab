from django.contrib import admin
from .models import TeamMember
from core.admin_base import BaseAdmin

@admin.register(TeamMember)
class TeamMemberAdmin(BaseAdmin):
    list_display = ['name', 'role', 'email', 'order', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['name', 'email']
    ordering = ['order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'role', 'photo', 'email', 'bio')
        }),
        ('Links', {
            'fields': ('linkedin_url', 'google_scholar_url')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
