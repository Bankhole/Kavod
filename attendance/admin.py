from django.contrib import admin

from .models import (
    AcademicSession,
    AttendanceHeader,
    AttendanceRecord,
    Student,
    StudentClass,
    Subject,
)


admin.site.register(AcademicSession)
admin.site.register(Subject)
admin.site.register(StudentClass)
admin.site.register(AttendanceHeader)
admin.site.register(AttendanceRecord)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'first_name', 'last_name', 'student_class', 'parent')
    list_filter = ('student_class',)
    search_fields = ('roll_number', 'first_name', 'last_name', 'parent__username', 'parent__email')
    autocomplete_fields = ('parent',)
