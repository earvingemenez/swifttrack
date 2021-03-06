from django.contrib import admin
from . models import Project, ProjectAssignment, WorkDiary


class ProjectsAdmin(admin.ModelAdmin):

    list_display = ['name', 'date_created',]
    list_filter = ['date_created']


class ProjectAssignmentAdmin(admin.ModelAdmin):

    list_display = ['employee', 'project', 'weekly_hours']

class WorkDiaryAdmin(admin.ModelAdmin):

    list_display = ('finished_task', 'date', 'hours', )
    list_filter = ['date', 'hours']

admin.site.register(Project, ProjectsAdmin)
admin.site.register(WorkDiary, WorkDiaryAdmin)
admin.site.register(ProjectAssignment, ProjectAssignmentAdmin)