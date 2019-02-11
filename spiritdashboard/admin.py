from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CompletedMission, Mission, MissionKey, User, Grade

class SpiritUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
            ('Spirit Data', {'fields': ('grade','points','avatar')}),
    )


admin.site.register(User, SpiritUserAdmin)
admin.site.register(Mission)
admin.site.register(MissionKey)
admin.site.register(Grade)
admin.site.register(CompletedMission)


