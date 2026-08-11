# Automated Candidate Evaluation System

A Python Django web application for entry-level hiring. Recruiters can post jobs and create assessments; candidates take tests and receive automated scores and feedback on areas to improve.

## Features

- **Recruiters**: Post jobs, create assessments with multiple-choice questions (manual or **AI-generated**), set time limits and passing scores, view candidate attempts
- **Candidates**: Take assessments within the time limit, see scores and pass/fail status, get detailed feedback on strengths and weak areas
- **Automated feedback**: Performance broken down by skill category with actionable improvement suggestions


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
