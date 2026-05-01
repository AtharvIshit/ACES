"""Custom decorators for role-based access."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def recruiter_required(view_func):
    """Ensure user has recruiter role."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.is_recruiter():
            messages.error(request, 'Access denied. Recruiter role required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def admin_required(view_func):
    """Ensure user is a superuser (admin). Returns 403 if not."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('<h1>403 — ACCESS DENIED</h1><p>Superuser privileges required.</p>')
        return view_func(request, *args, **kwargs)
    return _wrapped


def candidate_required(view_func):
    """Ensure user has candidate role (or allow recruiters to take tests)."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped
