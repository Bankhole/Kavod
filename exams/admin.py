from django.contrib import admin
from .models import Quiz, Question, Option, Result, UserAnswer

# Inline for Options to be edited directly on the Question admin page
class OptionInline(admin.TabularInline):
    model = Option
    extra = 4 # Display 4 empty option fields by default
    max_num = 4 # Limit to 4 options (standard MCQ)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'marks')
    list_filter = ('quiz',)
    search_fields = ('text',)
    inlines = [OptionInline] # Add the options inline

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_minutes')
    search_fields = ('title',)
    fieldsets = (
        (None, {
            'fields': ('title', 'duration'),
            'description': 'Set the quiz duration in minutes. Leave blank for no time limit.'
        }),
    )

    def duration_minutes(self, obj):
        return f"{obj.duration} min" if obj.duration is not None else 'No limit'
    duration_minutes.short_description = 'Duration'
    
# Register Result and UserAnswer for administrative review
admin.site.register(Result)
admin.site.register(UserAnswer)