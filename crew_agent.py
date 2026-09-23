```python
from crewai import Agent, Task, Crew, Process, LLM


def build_crew(api_key: str, model_name: str) -> Crew:

    llm = LLM(
        model=model_name,
        api_key=api_key,
        temperature=0.3,
    )

    resume_reviewer = Agent(
        role="Senior Technical Recruiter and Resume Coach",
        goal=(
            "Carefully compare a candidate's resume against a specific job "
            "description, and give honest, specific, and actionable feedback "
            "that helps the candidate improve their resume for THIS job."
        ),
        backstory=(
            "You have spent 15 years reviewing resumes and hiring for technical "
            "and business roles. You are known for being direct, fair, and "
            "detail-oriented. You NEVER invent skills, experience, tools, or "
            "qualifications that are not explicitly present in the resume text "
            "you are given. If something is missing, you clearly say it is "
            "missing rather than assuming the candidate might have it. Your "
            "feedback is always specific enough that the candidate knows "
            "exactly what to change."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
        cache=False,
    )

    review_task = Task(
        description=(
            "You are given a CANDIDATE RESUME and a TARGET JOB DESCRIPTION below.\n\n"
            "CANDIDATE RESUME:\n"
            "----------------\n"
            "{resume_text}\n"
            "----------------\n\n"
            "TARGET JOB DESCRIPTION:\n"
            "----------------\n"
            "{job_description}\n"
            "----------------\n\n"
            "Using ONLY information that is actually present in the resume text "
            "above, do the following. Do not assume or invent any skill, tool, "
            "certification, or experience that is not explicitly written in the "
            "resume, even if it seems likely the candidate has it.\n\n"
            "1. Give an overall match score from 0-100 and briefly justify it "
            "in 1-2 sentences.\n"
            "2. List the candidate's strongest matching qualifications.\n"
            "3. List important job requirements that are missing or weakly "
            "represented in the resume.\n"
            "4. Give 5-8 concrete, actionable recommendations to improve the "
            "resume for this specific job.\n"
            "5. Suggest 8-12 keywords taken from the job description that the "
            "candidate should naturally work into the resume when truthful.\n\n"
            "Format the answer in clean Markdown using exactly these headers:\n"
            "## Match Score\n"
            "## Matching Strengths\n"
            "## Gaps & Missing Requirements\n"
            "## Actionable Recommendations\n"
            "## ATS Keywords to Add"
        ),
        expected_output=(
            "A well-formatted Markdown report with the five sections listed "
            "above, grounded only in the actual resume text provided."
        ),
        agent=resume_reviewer,
    )

    crew = Crew(
        agents=[resume_reviewer],
        tasks=[review_task],
        process=Process.sequential,
        verbose=False,
    )

    return crew


def run_resume_review(
    api_key: str,
    resume_text: str,
    job_description: str,
    model_name: str,
) -> str:

    crew = build_crew(
        api_key=api_key,
        model_name=model_name,
    )

    result = crew.kickoff(
        inputs={
            "resume_text": resume_text,
            "job_description": job_description,
        }
    )

    return str(result)
```
