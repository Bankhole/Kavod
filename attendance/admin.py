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
admin.site.register(Student)
admin.site.register(AttendanceHeader)
admin.site.register(AttendanceRecord)
