# Register your models here.
from django.contrib import admin
from .models import Teacher, Subject, Classroom, TimeSlot, Schedule

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'subject', 'teacher', 'time_slot')
    list_filter = ('classroom', 'teacher', 'time_slot__day')
    search_fields = ('subject__name', 'teacher__first_name', 'teacher__last_name')

admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Classroom)
admin.site.register(TimeSlot)
