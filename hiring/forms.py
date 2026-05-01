"""Forms for the hiring app."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Job, Assessment, Question, QuestionOption, SkillCategory


class SignUpForm(UserCreationForm):
    """User registration with role selection."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    role = forms.ChoiceField(
        choices=[('', 'Select role')] + list(UserProfile.ROLE_CHOICES),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    organization = forms.CharField(max_length=200, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'organization')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': self.cleaned_data['role'], 'organization': self.cleaned_data.get('organization', '')}
            )
            if not _:
                profile.role = self.cleaned_data['role']
                profile.organization = self.cleaned_data.get('organization', '')
                profile.save()
        return user


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'department', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Job description'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Engineering'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Remote'}),
        }


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'description', 'duration_minutes', 'passing_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'skill_category', 'points', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'skill_category': forms.Select(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['option_text', 'is_correct', 'order']
        widgets = {
            'option_text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


QuestionOptionFormSet = forms.inlineformset_factory(
    Question, QuestionOption, form=QuestionOptionForm, extra=2, min_num=2, validate_min=True
)


class ProfileForm(forms.ModelForm):
    """Profile form for candidates - updates User and UserProfile."""
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['organization', 'phone', 'bio', 'resume', 'profile_picture']
        widgets = {
            'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company or institution'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief bio or summary'}),
            'resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.email = self.cleaned_data['email']
            profile.user.save()
            profile.save()
        return profile
