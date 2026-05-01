# Automated Candidate Evaluation System

A Python Django web application for entry-level hiring. Recruiters can post jobs and create assessments; candidates take tests and receive automated scores and feedback on areas to improve.

## Features

- **Recruiters**: Post jobs, create assessments with multiple-choice questions (manual or **AI-generated**), set time limits and passing scores, view candidate attempts
- **Candidates**: Take assessments within the time limit, see scores and pass/fail status, get detailed feedback on strengths and weak areas
- **Automated feedback**: Performance broken down by skill category with actionable improvement suggestions

## Quick Start

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. Run migrations:

   ```bash
   python manage.py migrate
   ```

3. Create an admin user (optional, for Django admin):

   ```bash
   python manage.py createsuperuser
   ```

4. Set up the Gemini API key for AI question generation (optional):
   - Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`
   - Or create `.env` with: `GEMINI_API_KEY=your_key_here`

5. Create skill categories (optional, for better feedback):

   - Go to http://127.0.0.1:8000/admin/ and add entries under **Skill Categories**
   - Assign categories to questions when creating them

6. Start the server:

   ```bash
   python manage.py runserver
   ```

7. Open http://127.0.0.1:8000/ and sign up. Choose **Recruiter** or **Candidate** when registering.

## Usage

### As a Recruiter

1. Sign up with role **Recruiter**
2. Post a job (title, description, department, location)
3. Create an assessment for the job (title, duration, passing score)
4. Add multiple-choice questions: use **Generate with AI** (powered by Google Gemini) or add manually; optionally assign skill categories
5. View candidate attempts and scores

### As a Candidate

1. Sign up with role **Candidate**
2. View available assessments on the dashboard
3. Start an assessment; a timer runs for the duration
4. Answer all questions and submit
5. View your score, pass/fail, and detailed feedback on areas to improve

## Tech Stack

- Python 3.10+
- Django 4.2
- SQLite (default; can switch to PostgreSQL for production)
