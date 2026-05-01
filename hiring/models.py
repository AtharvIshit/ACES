"""
Models for the Automated Candidate Evaluation System.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


def resume_upload_path(instance, filename):
    """Generate upload path for resumes: resumes/user_{id}/{filename}"""
    ext = filename.split('.')[-1] if '.' in filename else 'pdf'
    return f'resumes/user_{instance.user_id}/resume_{timezone.now().strftime("%Y%m%d_%H%M")}.{ext}'


def profile_picture_upload_path(instance, filename):
    """Generate upload path for profile pictures: profile_pics/user_{id}/{filename}"""
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    return f'profile_pics/user_{instance.user_id}/pic_{timezone.now().strftime("%Y%m%d_%H%M")}.{ext}'


class UserProfile(models.Model):
    """Extended user profile with role (recruiter or candidate)."""
    RECRUITER = 'R'
    CANDIDATE = 'C'
    ROLE_CHOICES = [(RECRUITER, 'Recruiter'), (CANDIDATE, 'Candidate')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default=CANDIDATE)
    organization = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    resume = models.FileField(upload_to=resume_upload_path, blank=True, null=True)
    profile_picture = models.ImageField(upload_to=profile_picture_upload_path, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_recruiter(self):
        return self.role == self.RECRUITER

    def is_candidate(self):
        return self.role == self.CANDIDATE


class Job(models.Model):
    """Job posting created by recruiters."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    department = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class SkillCategory(models.Model):
    """Categories for grouping questions (e.g., Python, SQL, Problem Solving)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Assessment(models.Model):
    """Assessment/test linked to a job."""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30, validators=[MinValueValidator(5), MaxValueValidator(180)])
    passing_score = models.PositiveIntegerField(default=60, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.job.title})"

    def total_questions(self):
        return self.questions.count()

    def total_points(self):
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    """Question in an assessment."""
    MULTIPLE_CHOICE = 'MC'
    CODING = 'CD'
    QUESTION_TYPE_CHOICES = [
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (CODING, 'Coding'),
    ]

    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('sql', 'SQL'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    skill_category = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPE_CHOICES, default=MULTIPLE_CHOICE)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    # Coding question fields
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python', blank=True)
    starter_code = models.TextField(blank=True, help_text='Pre-filled code template for the candidate')
    coding_instructions = models.TextField(blank=True, help_text='Detailed problem statement for coding questions')
    expected_output = models.TextField(blank=True, help_text='Reference expected output or solution description')

    class Meta:
        ordering = ['order', 'id']

    @property
    def is_coding(self):
        return self.question_type == self.CODING

    @property
    def is_mcq(self):
        return self.question_type == self.MULTIPLE_CHOICE

    def __str__(self):
        prefix = '[CODE] ' if self.is_coding else ''
        text = self.question_text[:50]
        return f"{prefix}{text}..." if len(self.question_text) > 50 else f"{prefix}{self.question_text}"


class QuestionOption(models.Model):
    """Answer option for multiple choice questions."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class CandidateAttempt(models.Model):
    """Record of a candidate taking an assessment."""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='attempts')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']
        unique_together = ['assessment', 'candidate']

    def __str__(self):
        return f"{self.candidate.username} - {self.assessment.title}"

    @property
    def is_complete(self):
        return self.completed_at is not None


class CodingTestCase(models.Model):
    """Test case for a coding question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField(help_text='Input for this test case')
    expected_output = models.TextField(help_text='Expected output for this test case')
    is_hidden = models.BooleanField(default=False, help_text='Hidden test cases are not shown to candidates')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"TestCase {self.order} for Q{self.question_id}"


class Answer(models.Model):
    """Candidate's answer to a question."""
    attempt = models.ForeignKey(CandidateAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='candidate_answers')
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True, related_name='selected_by')
    is_correct = models.BooleanField(null=True)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Coding question response fields
    code_response = models.TextField(blank=True, help_text='Submitted code for coding questions')
    ai_feedback = models.TextField(blank=True, help_text='AI evaluation feedback for coding answers')

    class Meta:
        unique_together = ['attempt', 'question']
