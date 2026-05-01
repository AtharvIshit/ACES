"""Admin Control Panel views for ACES."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    UserProfile, Job, Assessment, Question, CandidateAttempt, Answer, SkillCategory,
)
from .decorators import admin_required


# ─── Dashboard ───────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_dashboard(request):
    """System overview: key metrics + recent activity."""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    total_users = User.objects.count()
    total_recruiters = UserProfile.objects.filter(role=UserProfile.RECRUITER).count()
    total_candidates = UserProfile.objects.filter(role=UserProfile.CANDIDATE).count()
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_assessments = Assessment.objects.count()
    total_attempts = CandidateAttempt.objects.count()
    completed_attempts = CandidateAttempt.objects.filter(completed_at__isnull=False).count()
    passed_attempts = CandidateAttempt.objects.filter(passed=True).count()

    # Recent activity — last 10 completed attempts
    recent_attempts = (
        CandidateAttempt.objects
        .filter(completed_at__isnull=False)
        .select_related('candidate', 'assessment', 'assessment__job')
        .order_by('-completed_at')[:10]
    )

    # New users in last 30 days
    new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()

    # Average score across all completed attempts
    avg_score = CandidateAttempt.objects.filter(
        completed_at__isnull=False, percentage__isnull=False
    ).aggregate(avg=Avg('percentage'))['avg']

    # Pass rate
    pass_rate = (
        round(passed_attempts / completed_attempts * 100, 1)
        if completed_attempts > 0 else 0
    )

    # Daily attempt counts for the last 14 days (for sparkline)
    daily_data = []
    for i in range(13, -1, -1):
        day = (now - timedelta(days=i)).date()
        count = CandidateAttempt.objects.filter(
            completed_at__date=day
        ).count()
        daily_data.append({'date': day.strftime('%b %d'), 'count': count})

    import json
    daily_json = json.dumps(daily_data)

    return render(request, 'hiring/admin_dashboard.html', {
        'total_users': total_users,
        'total_recruiters': total_recruiters,
        'total_candidates': total_candidates,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_assessments': total_assessments,
        'total_attempts': total_attempts,
        'completed_attempts': completed_attempts,
        'passed_attempts': passed_attempts,
        'recent_attempts': recent_attempts,
        'new_users_30d': new_users_30d,
        'avg_score': avg_score,
        'pass_rate': pass_rate,
        'daily_json': daily_json,
    })


# ─── Users ───────────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_users(request):
    """List all users with search and role filter."""
    role_filter = request.GET.get('role', 'all')
    search = request.GET.get('q', '').strip()

    users = User.objects.select_related('profile').order_by('-date_joined')

    if role_filter == 'recruiter':
        users = users.filter(profile__role=UserProfile.RECRUITER)
    elif role_filter == 'candidate':
        users = users.filter(profile__role=UserProfile.CANDIDATE)

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    return render(request, 'hiring/admin_users.html', {
        'users': users,
        'role_filter': role_filter,
        'search': search,
    })


@login_required
@admin_required
def admin_user_detail(request, pk):
    """Single user deep-dive."""
    target_user = get_object_or_404(User, pk=pk)
    profile = getattr(target_user, 'profile', None)

    # Get their activity based on role
    if profile and profile.is_recruiter():
        jobs = Job.objects.filter(created_by=target_user).prefetch_related('assessments')
        attempts = None
    else:
        jobs = None
        attempts = CandidateAttempt.objects.filter(
            candidate=target_user
        ).select_related('assessment', 'assessment__job').order_by('-started_at')

    return render(request, 'hiring/admin_user_detail.html', {
        'target_user': target_user,
        'profile': profile,
        'jobs': jobs,
        'attempts': attempts,
    })


@login_required
@admin_required
@require_POST
def admin_user_toggle(request, pk):
    """Toggle a user's is_active status."""
    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, 'Cannot deactivate your own account.')
        return redirect('admin_user_detail', pk=pk)

    target_user.is_active = not target_user.is_active
    target_user.save()
    status = 'ACTIVATED' if target_user.is_active else 'DEACTIVATED'
    messages.success(request, f'User {target_user.username} has been {status}.')
    return redirect('admin_user_detail', pk=pk)


# ─── Jobs ────────────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_jobs(request):
    """All jobs across all recruiters."""
    status_filter = request.GET.get('status', 'all')
    jobs = Job.objects.select_related('created_by').annotate(
        assessment_count=Count('assessments'),
    ).order_by('-created_at')

    if status_filter == 'active':
        jobs = jobs.filter(is_active=True)
    elif status_filter == 'inactive':
        jobs = jobs.filter(is_active=False)

    return render(request, 'hiring/admin_jobs.html', {
        'jobs': jobs,
        'status_filter': status_filter,
    })


# ─── Assessments ─────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_assessments(request):
    """All assessments with stats."""
    assessments = Assessment.objects.select_related('job', 'job__created_by').annotate(
        question_count=Count('questions'),
        attempt_count=Count('attempts'),
        avg_score=Avg('attempts__percentage'),
    ).order_by('-created_at')

    return render(request, 'hiring/admin_assessments.html', {
        'assessments': assessments,
    })


# ─── Attempts ────────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_attempts(request):
    """All candidate attempts with filters."""
    status_filter = request.GET.get('status', 'all')
    attempts = (
        CandidateAttempt.objects
        .select_related('candidate', 'assessment', 'assessment__job')
        .order_by('-started_at')
    )

    if status_filter == 'passed':
        attempts = attempts.filter(passed=True)
    elif status_filter == 'failed':
        attempts = attempts.filter(passed=False)
    elif status_filter == 'in_progress':
        attempts = attempts.filter(completed_at__isnull=True)

    return render(request, 'hiring/admin_attempts.html', {
        'attempts': attempts,
        'status_filter': status_filter,
    })


@login_required
@admin_required
def admin_attempt_detail(request, pk):
    """Forensic deep-dive into a single attempt."""
    attempt = get_object_or_404(
        CandidateAttempt.objects.select_related(
            'candidate', 'assessment', 'assessment__job'
        ),
        pk=pk,
    )
    answers = attempt.answers.select_related(
        'question', 'selected_option', 'question__skill_category'
    ).prefetch_related('question__options').order_by('question__order')

    return render(request, 'hiring/admin_attempt_detail.html', {
        'attempt': attempt,
        'answers': answers,
    })


# ─── Proctoring ──────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_proctoring(request):
    """Proctoring log viewer — mounts the BrutalistAdminQuery React component."""
    return render(request, 'hiring/admin_proctoring.html')
