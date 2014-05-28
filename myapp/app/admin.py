from django.contrib import admin
from app.models import Staff,Role,Group,Task,Comment,Meeting,Notice,Calendar
from mptt.admin import ModelAdmin

admin.site.register(Staff)
admin.site.register(Role)
admin.site.register(Group)
admin.site.register(Task, ModelAdmin)
admin.site.register(Comment)
admin.site.register(Meeting)
admin.site.register(Notice)
admin.site.register(Calendar)
