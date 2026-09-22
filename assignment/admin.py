# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from .models import Assignment, Submission

class SubmissionInline(admin.TabularInline):
    """Allows viewing student submissions directly inside an Assignment detail view."""
    model = Submission
    extra = 0
    readonly_fields = ('student', 'submission_text', 'file_download_link', 'submitted_at')
    fields = ('student', 'submission_text', 'file_download_link', 'submitted_at', 'grade')
    can_delete = False

    def file_download_link(self, obj):
        if obj.file_upload:
            return format_html('<a href="{}" target="_blank">Download File</a>', obj.file_upload.url)
        return "No file attached"
    file_download_link.short_description = "Attachment"


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'student_class', 'due_date', 'created_at', 'total_submissions')
    list_filter = ('student_class', 'due_date', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-due_date',)
    inlines = [SubmissionInline]

    def total_submissions(self, obj):
        return obj.submissions.count()
    total_submissions.short_description = "Submissions"


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'grade', 'has_file')
    list_filter = ('assignment', 'submitted_at', 'grade')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'assignment__title')
    list_editable = ('grade',)  # Teachers can quickly grade from the list view
    readonly_fields = ('assignment', 'student', 'submission_text', 'file_upload', 'submitted_at')

    def has_file(self, obj):
        return bool(obj.file_upload)
    has_file.boolean = True
    has_file.short_description = "File Attached"