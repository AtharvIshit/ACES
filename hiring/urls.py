"""URL configuration for hiring app."""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),

    # Recruiter: Jobs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/new/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),
    path('jobs/<int:pk>/assessment/new/', views.assessment_create, name='assessment_create'),

    # Recruiter: Assessments
    path('assessments/<int:pk>/', views.assessment_detail, name='assessment_detail'),
    path('assessments/<int:pk>/delete/', views.assessment_delete, name='assessment_delete'),
    path('assessments/<int:pk>/questions/', views.assessment_questions, name='assessment_questions'),
    path('assessments/<int:pk>/questions/add/', views.question_add, name='question_add'),
    path('assessments/<int:pk>/questions/generate/', views.questions_generate_ai, name='questions_generate_ai'),
    path('assessments/<int:assessment_pk>/attempts/', views.attempt_list, name='attempt_list'),

    # Recruiter: Candidates
    path('candidate/<int:pk>/', views.candidate_profile, name='candidate_profile'),

    # Recruiter: Questions
    path('questions/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('questions/<int:pk>/delete/', views.question_delete, name='question_delete'),

    # Candidate: Take assessment
    path('assessments/<int:pk>/start/', views.assessment_start, name='assessment_start'),
    path('attempt/<int:pk>/', views.attempt_take, name='attempt_take'),
    path('attempt/<int:pk>/submit/', views.attempt_submit, name='attempt_submit'),
    path('attempt/<int:pk>/result/', views.attempt_result, name='attempt_result'),

    # Admin Control Panel
    path('control/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('control/users/', admin_views.admin_users, name='admin_users'),
    path('control/users/<int:pk>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('control/users/<int:pk>/toggle/', admin_views.admin_user_toggle, name='admin_user_toggle'),
    path('control/jobs/', admin_views.admin_jobs, name='admin_jobs'),
    path('control/assessments/', admin_views.admin_assessments, name='admin_assessments'),
    path('control/attempts/', admin_views.admin_attempts, name='admin_attempts'),
    path('control/attempts/<int:pk>/', admin_views.admin_attempt_detail, name='admin_attempt_detail'),
    path('control/proctoring/', admin_views.admin_proctoring, name='admin_proctoring'),
]

