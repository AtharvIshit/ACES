"""
AI-powered question generation using Google Gemini API.
Supports MCQ, Coding, and Mixed question types.
"""
from __future__ import annotations

import json
import re
from typing import List, Dict, Any, Optional

import requests
from django.conf import settings


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _gemini_api_key() -> str:
    return getattr(settings, "GEMINI_API_KEY", "")


def _call_gemini(system_instruction: str, prompt: str, max_tokens: int = 4096, temperature: float = 0.3) -> str:
    """Send a prompt to Gemini and return the text response."""
    api_key = _gemini_api_key()
    if not api_key:
        raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY in .env")

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "contents": [
                {
                    "parts": [
                        {"text": system_instruction + "\n\n" + prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        },
        timeout=90,
    )
    response.raise_for_status()
    data = response.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return parts[0].get("text", "") if parts else ""


def _extract_json(raw: str) -> Any:
    """Extract JSON from raw text, handling markdown code blocks."""
    text = raw.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


# ---------------------------------------------------------------------------
# MCQ Generation
# ---------------------------------------------------------------------------

def generate_questions(
    job_title: str,
    job_description: str,
    assessment_title: str,
    num_questions: int = 5,
    topics: str = "",
    question_type: str = "mcq",
    language: str = "python",
) -> List[Dict[str, Any]]:
    """
    Generate assessment questions.
    question_type: 'mcq', 'coding', or 'mixed'
    Returns list of question dicts (format depends on type).
    """
    if question_type == "coding":
        return generate_coding_questions(
            job_title=job_title,
            job_description=job_description,
            assessment_title=assessment_title,
            num_questions=num_questions,
            topics=topics,
            language=language,
        )
    elif question_type == "mixed":
        mcq_count = max(1, num_questions // 2)
        coding_count = num_questions - mcq_count
        mcq_results = _generate_mcq(
            job_title=job_title,
            job_description=job_description,
            assessment_title=assessment_title,
            num_questions=mcq_count,
            topics=topics,
        )
        coding_results = generate_coding_questions(
            job_title=job_title,
            job_description=job_description,
            assessment_title=assessment_title,
            num_questions=coding_count,
            topics=topics,
            language=language,
        )
        # If either errored, still return results from the other
        mcq_ok = mcq_results and not (isinstance(mcq_results[0], dict) and mcq_results[0].get("error"))
        coding_ok = coding_results and not (isinstance(coding_results[0], dict) and coding_results[0].get("error"))
        results = []
        if mcq_ok:
            results.extend(mcq_results)
        if coding_ok:
            results.extend(coding_results)
        if not results:
            return mcq_results or coding_results  # Return whichever has the error
        return results
    else:
        return _generate_mcq(
            job_title=job_title,
            job_description=job_description,
            assessment_title=assessment_title,
            num_questions=num_questions,
            topics=topics,
        )


def _generate_mcq(
    job_title: str,
    job_description: str,
    assessment_title: str,
    num_questions: int = 5,
    topics: str = "",
) -> List[Dict[str, Any]]:
    """Generate multiple-choice questions."""
    api_key = _gemini_api_key()
    if not api_key:
        return [{"error": "Gemini API key not configured. Set GEMINI_API_KEY in .env"}]

    topic_hint = f" Focus on these topics: {topics}." if topics else ""

    prompt = f"""Generate {num_questions} multiple-choice assessment questions for an entry-level hiring test.

Context:
- Job: {job_title}
- Job description: {job_description}
- Assessment: {assessment_title}
{topic_hint}

Requirements:
- Each question must have exactly 4 options (A, B, C, D).
- Mark exactly one correct answer per question.
- Questions should be appropriate for entry-level candidates.
- Return ONLY valid JSON, no markdown or extra text.

Format your response as a JSON array like this:
[
  {{"question_text": "What is...?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_index": 0}},
  ...
]

Return the JSON array now:"""

    try:
        content = _call_gemini(
            "You are an expert at creating fair, clear multiple-choice assessment questions. Always respond with valid JSON only.",
            prompt,
        )
        return _parse_mcq_questions(content)
    except ValueError as e:
        return [{"error": str(e)}]
    except requests.RequestException as e:
        return [{"error": f"API request failed: {str(e)}"}]
    except (KeyError, IndexError, TypeError) as e:
        return [{"error": f"Unexpected API response: {str(e)}"}]


def _parse_mcq_questions(raw: str) -> List[Dict[str, Any]]:
    """Parse raw API response into list of MCQ question dicts."""
    try:
        parsed = _extract_json(raw)
        if not isinstance(parsed, list):
            return [{"error": "API did not return a list of questions"}]

        result = []
        for i, item in enumerate(parsed):
            if isinstance(item, dict) and "error" in item:
                result.append(item)
                continue
            q = _normalize_mcq_question(item, i)
            if q:
                result.append(q)
        return result
    except json.JSONDecodeError as e:
        return [{"error": f"Could not parse AI response as JSON: {e}"}]


def _normalize_mcq_question(item: dict, index: int) -> Optional[Dict[str, Any]]:
    """Convert API item to our standard MCQ format."""
    if not isinstance(item, dict):
        return None
    text = item.get("question_text") or item.get("question") or item.get("text") or ""
    options = item.get("options") or item.get("choices") or []
    correct = item.get("correct_index", item.get("correct_answer", 0))

    if not text or len(options) < 2:
        return None

    if isinstance(correct, str) and correct.upper() in ("A", "B", "C", "D"):
        correct = ord(correct.upper()) - ord("A")
    try:
        correct = int(correct)
    except (TypeError, ValueError):
        correct = 0
    if correct < 0 or correct >= len(options):
        correct = 0

    return {
        "type": "mcq",
        "question_text": str(text).strip(),
        "options": [str(o).strip() for o in options[:4]],
        "correct_index": correct,
    }


# ---------------------------------------------------------------------------
# Coding Question Generation
# ---------------------------------------------------------------------------

def generate_coding_questions(
    job_title: str,
    job_description: str,
    assessment_title: str,
    num_questions: int = 3,
    topics: str = "",
    language: str = "python",
) -> List[Dict[str, Any]]:
    """Generate coding assessment questions with test cases."""
    api_key = _gemini_api_key()
    if not api_key:
        return [{"error": "Gemini API key not configured. Set GEMINI_API_KEY in .env"}]

    topic_hint = f" Focus on these topics: {topics}." if topics else ""

    lang_templates = {
        "python": 'def solution():\n    # Your code here\n    pass',
        "javascript": 'function solution() {\n    // Your code here\n}',
        "java": 'public class Solution {\n    public static void main(String[] args) {\n        // Your code here\n    }\n}',
        "cpp": '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code here\n    return 0;\n}',
        "sql": '-- Write your SQL query here\nSELECT',
    }

    prompt = f"""Generate {num_questions} coding assessment questions for an entry-level hiring test.

Context:
- Job: {job_title}
- Job description: {job_description}
- Assessment: {assessment_title}
- Programming language: {language}
{topic_hint}

Requirements:
- Each question should be a self-contained coding problem.
- Provide clear problem statements with input/output examples.
- Include 2-3 test cases per question (mix of visible and hidden).
- Provide starter code in {language} as a template.
- Questions should be appropriate for entry-level candidates.
- Return ONLY valid JSON, no markdown or extra text.

Format your response as a JSON array like this:
[
  {{
    "question_text": "Short problem title",
    "coding_instructions": "Detailed problem statement explaining what to implement, input format, output format, constraints, and examples.",
    "language": "{language}",
    "starter_code": "{lang_templates.get(language, lang_templates['python'])}",
    "test_cases": [
      {{"input": "example input", "expected_output": "expected output", "is_hidden": false}},
      {{"input": "hidden input", "expected_output": "hidden output", "is_hidden": true}}
    ],
    "expected_output": "Brief description of what a correct solution should do"
  }},
  ...
]

Return the JSON array now:"""

    try:
        content = _call_gemini(
            "You are an expert at creating fair, practical coding assessment questions. Always respond with valid JSON only.",
            prompt,
            max_tokens=8192,
            temperature=0.4,
        )
        return _parse_coding_questions(content, language)
    except ValueError as e:
        return [{"error": str(e)}]
    except requests.RequestException as e:
        return [{"error": f"API request failed: {str(e)}"}]
    except (KeyError, IndexError, TypeError) as e:
        return [{"error": f"Unexpected API response: {str(e)}"}]


def _parse_coding_questions(raw: str, default_language: str = "python") -> List[Dict[str, Any]]:
    """Parse raw API response into list of coding question dicts."""
    try:
        parsed = _extract_json(raw)
        if not isinstance(parsed, list):
            return [{"error": "API did not return a list of questions"}]

        result = []
        for item in parsed:
            if isinstance(item, dict) and "error" in item:
                result.append(item)
                continue
            q = _normalize_coding_question(item, default_language)
            if q:
                result.append(q)
        return result
    except json.JSONDecodeError as e:
        return [{"error": f"Could not parse AI response as JSON: {e}"}]


def _normalize_coding_question(item: dict, default_language: str) -> Optional[Dict[str, Any]]:
    """Convert API item to our standard coding question format."""
    if not isinstance(item, dict):
        return None

    text = item.get("question_text") or item.get("title") or item.get("text") or ""
    instructions = item.get("coding_instructions") or item.get("description") or item.get("problem_statement") or ""
    language = item.get("language", default_language) or default_language
    starter = item.get("starter_code") or item.get("template") or ""
    expected = item.get("expected_output") or item.get("solution_description") or ""
    test_cases_raw = item.get("test_cases") or item.get("tests") or []

    if not text or not instructions:
        return None

    test_cases = []
    for tc in test_cases_raw:
        if isinstance(tc, dict):
            test_cases.append({
                "input": str(tc.get("input", "")).strip(),
                "expected_output": str(tc.get("expected_output", tc.get("output", ""))).strip(),
                "is_hidden": bool(tc.get("is_hidden", False)),
            })

    return {
        "type": "coding",
        "question_text": str(text).strip(),
        "coding_instructions": str(instructions).strip(),
        "language": str(language).strip().lower(),
        "starter_code": str(starter).strip(),
        "expected_output": str(expected).strip(),
        "test_cases": test_cases,
    }


# ---------------------------------------------------------------------------
# AI Code Evaluation
# ---------------------------------------------------------------------------

def evaluate_code_with_ai(
    question_text: str,
    coding_instructions: str,
    language: str,
    starter_code: str,
    candidate_code: str,
    test_cases: List[Dict[str, str]],
    max_points: int = 5,
) -> Dict[str, Any]:
    """
    Use Gemini to evaluate candidate's code submission.
    Returns: {"score": int, "max_score": int, "feedback": str, "passed": bool}
    """
    api_key = _gemini_api_key()
    if not api_key:
        return {"score": 0, "max_score": max_points, "feedback": "AI evaluation unavailable — API key not configured.", "passed": False}

    test_cases_str = ""
    for i, tc in enumerate(test_cases):
        test_cases_str += f"\nTest Case {i+1}:\n  Input: {tc.get('input', 'N/A')}\n  Expected Output: {tc.get('expected_output', 'N/A')}\n"

    prompt = f"""Evaluate the following candidate code submission for a coding assessment.

**Problem:** {question_text}

**Problem Statement:**
{coding_instructions}

**Language:** {language}

**Starter Code Provided:**
```{language}
{starter_code}
```

**Candidate's Code:**
```{language}
{candidate_code}
```

**Test Cases:**
{test_cases_str}

**Evaluation Criteria (score out of {max_points}):**
1. **Correctness** — Does the code solve the problem? Would it pass the test cases?
2. **Code Quality** — Is the code clean, readable, and well-structured?
3. **Edge Cases** — Does the code handle edge cases?
4. **Efficiency** — Is the approach reasonably efficient?

**Respond with ONLY valid JSON in this exact format:**
{{
  "score": <integer 0-{max_points}>,
  "correctness": "<brief assessment of correctness>",
  "quality": "<brief assessment of code quality>",
  "feedback": "<2-3 sentences of constructive feedback for the candidate>"
}}"""

    try:
        content = _call_gemini(
            "You are a strict but fair code reviewer for technical hiring assessments. Evaluate code objectively. Always respond with valid JSON only.",
            prompt,
            max_tokens=2048,
            temperature=0.2,
        )
        result = _extract_json(content)
        if not isinstance(result, dict):
            return {"score": 0, "max_score": max_points, "feedback": "Could not parse evaluation.", "passed": False}

        score = min(max_points, max(0, int(result.get("score", 0))))
        correctness = result.get("correctness", "")
        quality = result.get("quality", "")
        feedback = result.get("feedback", "No feedback available.")

        full_feedback = f"Score: {score}/{max_points}\n"
        if correctness:
            full_feedback += f"Correctness: {correctness}\n"
        if quality:
            full_feedback += f"Code Quality: {quality}\n"
        full_feedback += f"Feedback: {feedback}"

        return {
            "score": score,
            "max_score": max_points,
            "feedback": full_feedback,
            "passed": score >= (max_points * 0.6),
        }
    except Exception as e:
        return {
            "score": 0,
            "max_score": max_points,
            "feedback": f"AI evaluation failed: {str(e)}",
            "passed": False,
        }
