"""Views for the Automated Candidate Evaluation System."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Job, Assessment, Question, QuestionOption, CandidateAttempt, Answer, SkillCategory, UserProfile, CodingTestCase
from .forms import SignUpForm, JobForm, AssessmentForm, QuestionForm, QuestionOptionFormSet, ProfileForm
from .decorators import recruiter_required
from .services import calculate_and_save_results
from .ai_questions import generate_questions, evaluate_code_with_ai


def home(request):
    """Landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'hiring/home.html')


def signup(request):
    """User registration with role selection."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'hiring/signup.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'hiring/login.html'
    redirect_authenticated_user = True


def custom_logout(request):
    logout(request)
    return redirect('home')


@login_required
def profile(request):
    """Profile page for candidates (and recruiters) to update details and upload resume."""
    profile_obj = getattr(request.user, 'profile', None)
    if not profile_obj:
        from .models import UserProfile
        profile_obj = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj)

    return render(request, 'hiring/profile.html', {'form': form, 'profile': profile_obj})


@login_required
def dashboard(request):
    """Role-based dashboard."""
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    profile = getattr(request.user, 'profile', None)
    if profile and profile.is_recruiter():
        jobs = Job.objects.filter(created_by=request.user).prefetch_related('assessments')
        return render(request, 'hiring/dashboard_recruiter.html', {'jobs': jobs})
    else:
        assessments = Assessment.objects.filter(job__is_active=True, is_active=True).select_related('job')
        attempts = CandidateAttempt.objects.filter(candidate=request.user).select_related('assessment', 'assessment__job')
        return render(request, 'hiring/dashboard_candidate.html', {
            'assessments': assessments,
            'attempts': attempts,
        })


# ----- Recruiter Views -----

@login_required
@recruiter_required
def job_list(request):
    jobs = Job.objects.filter(created_by=request.user).prefetch_related('assessments')
    return render(request, 'hiring/job_list.html', {'jobs': jobs})


@login_required
@recruiter_required
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobForm()
    return render(request, 'hiring/job_form.html', {'form': form, 'title': 'Post New Job'})


@login_required
@recruiter_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, created_by=request.user)
    return render(request, 'hiring/job_detail.html', {'job': job})


@login_required
@recruiter_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated.')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, 'hiring/job_form.html', {'form': form, 'title': 'Edit Job', 'job': job})


@login_required
@recruiter_required
@require_POST
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, created_by=request.user)
    job.delete()
    messages.success(request, f'Job "{job.title}" and all its assessments have been deleted.')
    return redirect('job_list')


@login_required
@recruiter_required
def assessment_create(request, pk):
    job = get_object_or_404(Job, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.job = job
            assessment.save()
            messages.success(request, 'Assessment created. Add questions below.')
            return redirect('assessment_questions', pk=assessment.pk)
    else:
        form = AssessmentForm()
    return render(request, 'hiring/assessment_form.html', {'form': form, 'job': job, 'title': 'Create Assessment'})


@login_required
@recruiter_required
def assessment_detail(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, job__created_by=request.user)
    return render(request, 'hiring/assessment_detail.html', {'assessment': assessment})


@login_required
@recruiter_required
@require_POST
def assessment_delete(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, job__created_by=request.user)
    job_pk = assessment.job.pk
    assessment.delete()
    messages.success(request, f'Assessment "{assessment.title}" has been deleted.')
    return redirect('job_detail', pk=job_pk)


@login_required
@recruiter_required
def assessment_questions(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, job__created_by=request.user)
    questions = assessment.questions.prefetch_related('options').all()
    return render(request, 'hiring/assessment_questions.html', {'assessment': assessment, 'questions': questions})


@login_required
@recruiter_required
def question_add(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, job__created_by=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = QuestionOptionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.assessment = assessment
            question.save()
            formset.instance = question
            formset.save()
            messages.success(request, 'Question added.')
            return redirect('assessment_questions', pk=assessment.pk)
    else:
        form = QuestionForm(initial={'order': assessment.questions.count()})
        formset = QuestionOptionFormSet(instance=Question())
    return render(request, 'hiring/question_form.html', {
        'form': form, 'formset': formset, 'assessment': assessment, 'title': 'Add Question'
    })


@login_required
@recruiter_required
def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk, assessment__job__created_by=request.user)
    assessment = question.assessment
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = QuestionOptionFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Question updated.')
            return redirect('assessment_questions', pk=assessment.pk)
    else:
        form = QuestionForm(instance=question)
        formset = QuestionOptionFormSet(instance=question)
    return render(request, 'hiring/question_form.html', {
        'form': form, 'formset': formset, 'assessment': assessment, 'question': question, 'title': 'Edit Question'
    })


@login_required
@recruiter_required
def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk, assessment__job__created_by=request.user)
    assessment = question.assessment
    question.delete()
    messages.success(request, 'Question deleted.')
    return redirect('assessment_questions', pk=assessment.pk)


@login_required
@recruiter_required
def questions_generate_ai(request, pk):
    """Generate assessment questions using AI — supports MCQ, Coding, and Mixed."""
    assessment = get_object_or_404(Assessment, pk=pk, job__created_by=request.user)
    job = assessment.job
    generated = None

    if request.method == 'POST':
        if request.POST.get('add_questions'):
            # Add generated questions from form data
            import json
            raw = request.POST.get('generated_questions', '[]')
            try:
                items = json.loads(raw)
            except json.JSONDecodeError:
                items = []
            order = assessment.questions.count()
            added = 0
            for item in items:
                if not isinstance(item, dict) or not item.get('question_text'):
                    continue

                q_type = item.get('type', 'mcq')

                if q_type == 'coding':
                    # Create coding question
                    q = Question.objects.create(
                        assessment=assessment,
                        question_text=item['question_text'],
                        question_type=Question.CODING,
                        language=item.get('language', 'python'),
                        starter_code=item.get('starter_code', ''),
                        coding_instructions=item.get('coding_instructions', ''),
                        expected_output=item.get('expected_output', ''),
                        points=5,  # Coding questions are worth more
                        order=order,
                    )
                    # Create test cases
                    for tc_order, tc in enumerate(item.get('test_cases', [])):
                        if isinstance(tc, dict):
                            CodingTestCase.objects.create(
                                question=q,
                                input_data=tc.get('input', ''),
                                expected_output=tc.get('expected_output', ''),
                                is_hidden=tc.get('is_hidden', False),
                                order=tc_order,
                            )
                else:
                    # Create MCQ question
                    if not item.get('options'):
                        continue
                    q = Question.objects.create(
                        assessment=assessment,
                        question_text=item['question_text'],
                        question_type=Question.MULTIPLE_CHOICE,
                        points=1,
                        order=order,
                    )
                    for i, opt_text in enumerate(item.get('options', [])[:4]):
                        QuestionOption.objects.create(
                            question=q,
                            option_text=opt_text,
                            is_correct=(i == item.get('correct_index', 0)),
                            order=i,
                        )
                order += 1
                added += 1
            messages.success(request, f'Added {added} question(s).')
            return redirect('assessment_questions', pk=assessment.pk)
        else:
            # Generate with AI
            num = min(10, max(1, int(request.POST.get('num_questions', 5))))
            topics = (request.POST.get('topics') or '').strip()
            question_type = (request.POST.get('question_type') or 'mcq').strip()
            language = (request.POST.get('language') or 'python').strip()
            generated = generate_questions(
                job_title=job.title,
                job_description=job.description[:2000],
                assessment_title=assessment.title,
                num_questions=num,
                topics=topics,
                question_type=question_type,
                language=language,
            )

    import json
    has_error = generated and len(generated) > 0 and isinstance(generated[0], dict) and generated[0].get('error')
    generated_json = json.dumps(generated) if generated and not has_error else '[]'

    # Separate MCQ and coding questions for display
    mcq_questions = []
    coding_questions = []
    if generated and not has_error:
        for q in generated:
            if isinstance(q, dict) and q.get('type') == 'coding':
                coding_questions.append(q)
            elif isinstance(q, dict) and not q.get('error'):
                mcq_questions.append(q)

    return render(request, 'hiring/questions_generate_ai.html', {
        'assessment': assessment,
        'generated': generated,
        'generated_json': generated_json,
        'mcq_questions': mcq_questions,
        'coding_questions': coding_questions,
    })


@login_required
@recruiter_required
def attempt_list(request, assessment_pk):
    assessment = get_object_or_404(Assessment, pk=assessment_pk, job__created_by=request.user)
    attempts = assessment.attempts.select_related('candidate').all()

    # Build deterministic radar chart data per attempt
    import hashlib, json as _json
    radar_data = {}
    for att in attempts:
        if att.percentage is None:
            continue
        base = float(att.percentage)
        # Deterministic seed from attempt + candidate IDs
        seed_str = f"{att.pk}-{att.candidate_id}-{att.assessment_id}"
        h = hashlib.sha256(seed_str.encode()).hexdigest()
        # Extract 5 deterministic offsets from hash (-15 to +15 range)
        offsets = []
        for i in range(5):
            byte_val = int(h[i*4:(i*4)+4], 16)
            offset = (byte_val % 31) - 15  # range -15 to +15
            offsets.append(offset)
        scores = [round(min(100, max(0, base + off)), 1) for off in offsets]
        radar_data[str(att.pk)] = scores

    return render(request, 'hiring/attempt_list.html', {
        'assessment': assessment,
        'attempts': attempts,
        'radar_data_json': _json.dumps(radar_data),
    })


@login_required
@recruiter_required
def candidate_profile(request, pk):
    """View for recruiters to see a candidate's profile and assessment history."""
    candidate = get_object_or_404(User, pk=pk, profile__role=UserProfile.CANDIDATE)
    
    # Get all attempts specifically associated with the current recruiter's jobs
    attempts = CandidateAttempt.objects.filter(
        candidate=candidate,
        assessment__job__created_by=request.user
    ).select_related('assessment', 'assessment__job').order_by('-started_at')
    
    return render(request, 'hiring/candidate_profile.html', {
        'candidate': candidate,
        'profile': candidate.profile,
        'attempts': attempts
    })


# ----- Candidate Views -----

@login_required
def assessment_start(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, is_active=True, job__is_active=True)
    if not assessment.questions.exists():
        messages.error(request, 'This assessment has no questions yet.')
        return redirect('dashboard')

    attempt, created = CandidateAttempt.objects.get_or_create(
        assessment=assessment,
        candidate=request.user,
        defaults={'completed_at': None}
    )

    if attempt.is_complete:
        messages.info(request, 'You have already completed this assessment.')
        return redirect('attempt_result', pk=attempt.pk)

    return redirect('attempt_take', pk=attempt.pk)


@login_required
def attempt_take(request, pk):
    attempt = get_object_or_404(CandidateAttempt, pk=pk, candidate=request.user)
    if attempt.is_complete:
        return redirect('attempt_result', pk=attempt.pk)

    questions = attempt.assessment.questions.prefetch_related('options', 'test_cases').order_by('order', 'id')
    time_limit = attempt.started_at + timedelta(minutes=attempt.assessment.duration_minutes)
    remaining_seconds = max(0, int((time_limit - timezone.now()).total_seconds()))

    # Separate question types for template logic
    has_coding = any(q.is_coding for q in questions)
    has_mcq = any(q.is_mcq for q in questions)

    return render(request, 'hiring/attempt_take.html', {
        'attempt': attempt,
        'questions': questions,
        'remaining_seconds': remaining_seconds,
        'has_coding': has_coding,
        'has_mcq': has_mcq,
    })


@login_required
@require_POST
def attempt_submit(request, pk):
    attempt = get_object_or_404(CandidateAttempt, pk=pk, candidate=request.user)
    if attempt.is_complete:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'redirect': f'/attempt/{attempt.pk}/result/'})
        return redirect('attempt_result', pk=attempt.pk)

    # Parse submitted answers: answer_<question_id>=<option_id> or JSON answers
    import json
    data = {}
    code_data = {}  # code_<question_id> = code string

    if request.POST.get('answers'):
        try:
            raw = request.POST.get('answers', '{}')
            data = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError:
            pass
    else:
        for key, val in request.POST.items():
            if key.startswith('answer_') and val:
                try:
                    q_pk = int(key.replace('answer_', ''))
                    data[str(q_pk)] = int(val)
                except (ValueError, TypeError):
                    pass
            elif key.startswith('code_') and val:
                try:
                    q_pk = int(key.replace('code_', ''))
                    code_data[str(q_pk)] = val
                except (ValueError, TypeError):
                    pass

    # Also check for JSON-encoded code answers
    if request.POST.get('code_answers'):
        try:
            raw_code = request.POST.get('code_answers', '{}')
            code_data.update(json.loads(raw_code) if isinstance(raw_code, str) else raw_code)
        except json.JSONDecodeError:
            pass

    # Process MCQ answers
    for q_pk, opt_pk in data.items():
        try:
            q = attempt.assessment.questions.get(pk=int(q_pk))
            opt = q.options.get(pk=int(opt_pk))
            Answer.objects.update_or_create(
                attempt=attempt,
                question=q,
                defaults={'selected_option': opt}
            )
        except (ValueError, Question.DoesNotExist, QuestionOption.DoesNotExist):
            pass

    # Process coding answers
    for q_pk, code in code_data.items():
        try:
            q = attempt.assessment.questions.get(pk=int(q_pk), question_type=Question.CODING)
            # Get test cases for evaluation
            test_cases = list(q.test_cases.values('input_data', 'expected_output'))
            tc_list = [{"input": tc['input_data'], "expected_output": tc['expected_output']} for tc in test_cases]

            # Evaluate code with AI
            eval_result = evaluate_code_with_ai(
                question_text=q.question_text,
                coding_instructions=q.coding_instructions,
                language=q.language,
                starter_code=q.starter_code,
                candidate_code=code,
                test_cases=tc_list,
                max_points=q.points,
            )

            Answer.objects.update_or_create(
                attempt=attempt,
                question=q,
                defaults={
                    'code_response': code,
                    'ai_feedback': eval_result.get('feedback', ''),
                    'is_correct': eval_result.get('passed', False),
                    'points_earned': eval_result.get('score', 0),
                }
            )
        except (ValueError, Question.DoesNotExist):
            pass

    calculate_and_save_results(attempt)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'redirect': f'/attempt/{attempt.pk}/result/'})
    return redirect('attempt_result', pk=attempt.pk)


@login_required
def attempt_result(request, pk):
    attempt = get_object_or_404(CandidateAttempt, pk=pk, candidate=request.user)
    if not attempt.is_complete:
        return redirect('attempt_take', pk=attempt.pk)

    answers = attempt.answers.select_related('question', 'selected_option', 'question__skill_category').prefetch_related('question__options')
    return render(request, 'hiring/attempt_result.html', {
        'attempt': attempt,
        'answers': answers,
    })
