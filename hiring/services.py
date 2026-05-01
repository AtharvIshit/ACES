"""
Business logic for scoring and feedback generation.
"""
import re
from decimal import Decimal
from django.utils import timezone
from .models import CandidateAttempt, Answer


def calculate_and_save_results(attempt: CandidateAttempt) -> None:
    """
    Calculate score, percentage, pass/fail, and generate feedback for an attempt.
    """
    answers = attempt.answers.select_related('question', 'question__skill_category', 'selected_option')
    
    total_points = Decimal('0')
    earned_points = Decimal('0')
    category_scores = {}  # {category_name: (earned, total)}

    for answer in answers:
        question = answer.question
        total_points += question.points

        if question.is_coding:
            # Coding questions: score comes from AI evaluation stored in ai_feedback
            if answer.ai_feedback:
                score_match = re.search(r'Score:\s*(\d+)/(\d+)', answer.ai_feedback)
                if score_match:
                    ai_score = int(score_match.group(1))
                    ai_max = int(score_match.group(2))
                    # Scale AI score to question points
                    scaled = Decimal(str(ai_score)) / Decimal(str(ai_max)) * Decimal(str(question.points)) if ai_max > 0 else Decimal('0')
                    answer.points_earned = scaled
                    earned_points += scaled
                    answer.is_correct = ai_score >= (ai_max * 0.6)
                else:
                    answer.points_earned = Decimal('0')
                    answer.is_correct = False
            else:
                answer.points_earned = Decimal('0')
                answer.is_correct = False
        else:
            # MCQ: check selected option
            if answer.selected_option and answer.selected_option.is_correct:
                answer.is_correct = True
                answer.points_earned = question.points
                earned_points += question.points
            else:
                answer.is_correct = False
                answer.points_earned = Decimal('0')
        answer.save()

        # Track by skill category for feedback
        cat_name = question.skill_category.name if question.skill_category else 'General'
        if cat_name not in category_scores:
            category_scores[cat_name] = [Decimal('0'), Decimal('0')]
        category_scores[cat_name][1] += question.points
        if answer.is_correct:
            category_scores[cat_name][0] += question.points

    attempt.max_score = total_points
    attempt.score = earned_points
    attempt.percentage = (earned_points / total_points * 100) if total_points > 0 else Decimal('0')
    attempt.passed = attempt.percentage >= attempt.assessment.passing_score
    attempt.completed_at = timezone.now()
    attempt.feedback = _generate_feedback(attempt, category_scores)
    attempt.save()


def _generate_feedback(attempt: CandidateAttempt, category_scores: dict) -> str:
    """Generate actionable feedback based on performance across skill categories."""
    lines = []

    if attempt.passed:
        lines.append(f"Congratulations! You passed with {attempt.percentage:.1f}% (passing: {attempt.assessment.passing_score}%).")
    else:
        lines.append(f"You scored {attempt.percentage:.1f}%. The passing score is {attempt.assessment.passing_score}%. Keep practicing and try again!")

    # Skill-wise feedback
    weak_areas = []
    strong_areas = []

    for cat_name, (earned, total) in category_scores.items():
        if total > 0:
            pct = float(earned / total * 100)
            if pct < 50:
                weak_areas.append((cat_name, pct))
            elif pct >= 75:
                strong_areas.append((cat_name, pct))

    if weak_areas:
        lines.append("\n**Areas to improve:**")
        for name, pct in sorted(weak_areas, key=lambda x: x[1]):
            lines.append(f"• {name}: You scored {pct:.0f}%. Consider reviewing fundamentals and practicing more in this area.")

    if strong_areas:
        lines.append("\n**Strengths:**")
        for name, pct in sorted(strong_areas, key=lambda x: -x[1]):
            lines.append(f"• {name}: Strong performance at {pct:.0f}%.")

    lines.append("\n**General tips:**")
    if attempt.passed:
        lines.append("• Continue building on your strengths while maintaining your skills.")
    else:
        lines.append("• Focus on the weaker areas above. Practice with similar questions and revisit the concepts.")
        lines.append("• Take your time reading each question before answering.")
        lines.append("• You can retake the assessment to improve your score.")

    return "\n".join(lines)
