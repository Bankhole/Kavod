# Register your models here.
from django.contrib import admin
from .models import Category, Course, Module, Lesson, StudentEnrollment, LessonProgress

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    fieldsets = (
        (None, {'fields': ('title', 'lesson_type', 'order', 'is_preview')}),
        ('Recorded Video', {'fields': ('video_url', 'video_file', 'duration_minutes')}),
        ('Live Class Details', {'fields': ('live_start_time', 'live_meeting_url')}),
        ('Description', {'fields': ('description',)}),
    )

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    inlines = [LessonInline]

admin.site.register(Category)
admin.site.register(StudentEnrollment)
admin.site.register(LessonProgress)