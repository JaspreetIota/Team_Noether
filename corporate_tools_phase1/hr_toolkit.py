"""HR toolkit: resume parser, candidate ranking, JD generator, interview questions, and evaluations."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


COMMON_SKILLS = {
    "python", "excel", "sql", "power bi", "tableau", "javascript", "react", "node",
    "communication", "leadership", "sales", "marketing", "finance", "hr", "recruitment",
    "project management", "data analysis", "machine learning", "customer support",
}


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise SystemExit("Missing dependency for PDF resumes: pip install pypdf") from exc
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_resume(text: str) -> dict:
    email = re.findall(r"[\w.\-+]+@[\w.\-]+\.[A-Za-z]{2,}", text)
    phone = re.findall(r"(?:\+?\d[\d\s\-()]{7,}\d)", text)
    lowered = text.lower()
    skills = sorted(skill for skill in COMMON_SKILLS if skill in lowered)
    years = re.findall(r"(\d+)\+?\s*(?:years|yrs)", lowered)
    return {
        "email": email[0] if email else "",
        "phone": phone[0].strip() if phone else "",
        "skills": skills,
        "estimated_years_experience": max([int(value) for value in years], default=0),
        "word_count": len(re.findall(r"\w+", text)),
    }


def rank_candidates(resume_files: list[Path], job_description: str) -> list[dict]:
    jd_words = Counter(re.findall(r"[a-zA-Z][a-zA-Z+#.]{2,}", job_description.lower()))
    rankings = []
    for resume_file in resume_files:
        text = read_text(resume_file)
        resume_words = Counter(re.findall(r"[a-zA-Z][a-zA-Z+#.]{2,}", text.lower()))
        matched = sorted(set(jd_words) & set(resume_words))
        score = sum(jd_words[word] for word in matched)
        parsed = parse_resume(text)
        rankings.append({"candidate": resume_file.name, "score": score, "matched_keywords": matched[:30], **parsed})
    return sorted(rankings, key=lambda item: item["score"], reverse=True)


def generate_job_description(role: str, level: str, skills: list[str]) -> str:
    skill_text = ", ".join(skills) if skills else "role-specific tools and business skills"
    return f"""# {level.title()} {role}

## About the Role
We are looking for a {level.lower()} {role} to help our team deliver high-quality business outcomes.

## Responsibilities
- Own day-to-day execution for {role} workstreams
- Collaborate with cross-functional teams and stakeholders
- Track progress, communicate risks, and improve processes
- Prepare reports, documentation, and recommendations

## Required Skills
- {skill_text}
- Clear written and verbal communication
- Strong ownership and problem-solving ability

## Evaluation Criteria
- Relevant experience
- Technical and business skill match
- Communication quality
- Culture and teamwork fit
"""


def generate_questions(role: str, skills: list[str], count: int = 10) -> list[str]:
    base = [
        f"Tell us about your experience as a {role}.",
        "Describe a project where you solved a difficult business problem.",
        "How do you prioritize work when several tasks are urgent?",
        "Tell us about a mistake you made and how you handled it.",
        "How do you communicate progress to stakeholders?",
    ]
    skill_questions = [f"How have you used {skill} in a real work situation?" for skill in skills]
    return (base + skill_questions)[:count]


def employee_evaluation_template(role: str) -> str:
    return f"""# Employee Evaluation Template: {role}

Employee Name:
Manager:
Review Period:

## Ratings
- Job Knowledge: /5
- Quality of Work: /5
- Productivity: /5
- Communication: /5
- Teamwork: /5
- Ownership: /5

## Achievements
- 

## Improvement Areas
- 

## Goals for Next Period
- 

## Manager Summary

## Employee Comments
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="HR toolkit for common recruiting and employee workflows.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_cmd = subparsers.add_parser("parse-resume")
    parse_cmd.add_argument("resume", type=Path)
    parse_cmd.add_argument("--output", type=Path)

    rank_cmd = subparsers.add_parser("rank-candidates")
    rank_cmd.add_argument("job_description", type=Path)
    rank_cmd.add_argument("resumes", nargs="+", type=Path)
    rank_cmd.add_argument("--output", type=Path, default=Path("candidate_ranking.json"))

    jd_cmd = subparsers.add_parser("job-description")
    jd_cmd.add_argument("--role", required=True)
    jd_cmd.add_argument("--level", default="Mid-level")
    jd_cmd.add_argument("--skills", nargs="*", default=[])
    jd_cmd.add_argument("--output", type=Path)

    q_cmd = subparsers.add_parser("interview-questions")
    q_cmd.add_argument("--role", required=True)
    q_cmd.add_argument("--skills", nargs="*", default=[])
    q_cmd.add_argument("--count", type=int, default=10)
    q_cmd.add_argument("--output", type=Path)

    eval_cmd = subparsers.add_parser("evaluation-template")
    eval_cmd.add_argument("--role", required=True)
    eval_cmd.add_argument("--output", type=Path)

    args = parser.parse_args()

    if args.command == "parse-resume":
        result = json.dumps(parse_resume(read_text(args.resume)), indent=2)
    elif args.command == "rank-candidates":
        result = json.dumps(rank_candidates(args.resumes, read_text(args.job_description)), indent=2)
    elif args.command == "job-description":
        result = generate_job_description(args.role, args.level, args.skills)
    elif args.command == "interview-questions":
        result = "\n".join(f"{index}. {question}" for index, question in enumerate(generate_questions(args.role, args.skills, args.count), 1))
    elif args.command == "evaluation-template":
        result = employee_evaluation_template(args.role)
    else:
        raise ValueError(args.command)

    output = getattr(args, "output", None)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result + "\n", encoding="utf-8")
        print(output)
    else:
        print(result)


if __name__ == "__main__":
    main()

