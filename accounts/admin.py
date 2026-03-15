from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(ModelAdmin, UserAdmin):
    list_display  = ['username', 'email', 'first_name', 'last_name',
                     'is_active', 'get_groups']
    list_filter   = ['is_active', 'groups']

    @admin.display(description='Роли')
    def get_groups(self, obj):
        return ', '.join(obj.groups.values_list('name', flat=True)) or '—'