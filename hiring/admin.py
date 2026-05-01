"""Admin configuration for hiring app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Job, SkillCategory, Assessment, Question, QuestionOption, CandidateAttempt, Answer, CodingTestCase


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
UserAdmin.inlines = [UserProfileInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'job', 'duration_minutes', 'passing_score', 'is_active']
    list_filter = ['is_active']
    inlines = [QuestionInline]


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 2


class CodingTestCaseInline(admin.TabularInline):
    model = CodingTestCase
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'assessment', 'skill_category', 'question_type', 'points', 'order']
    list_filter = ['question_type']
    inlines = [QuestionOptionInline, CodingTestCaseInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    readonly_fields = ['question', 'selected_option', 'is_correct', 'points_earned']
    can_delete = False
    extra = 0
    max_num = 0


class CandidateAttemptAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'assessment', 'started_at', 'completed_at', 'score', 'percentage', 'passed']
    list_filter = ['passed', 'completed_at']
    readonly_fields = ['started_at', 'completed_at', 'score', 'max_score', 'percentage', 'passed']
    inlines = [AnswerInline]


admin.site.register(UserProfile)
admin.site.register(Job)
admin.site.register(SkillCategory)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionOption)
admin.site.register(CandidateAttempt, CandidateAttemptAdmin)
admin.site.register(Answer)
admin.site.register(CodingTestCase)
