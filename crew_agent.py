"""
crew_agent.py
--------------
This file defines the "brain" of the app: a single CrewAI agent that compares
a resume against a job description and writes a structured feedback report.

Students: you don't need to touch this file to run the app. If you want to
change how the agent thinks or what it outputs, edit the text inside
`build_crew()` below.
"""

from crewai import Agent, Task, Crew, Process, LLM


def build_crew(api_key: str, model_name: str) -> Crew:
    """
    Builds and returns a CrewAI Crew containing exactly one agent and one task.

    api_key    -> your Groq API key (read from Streamlit secrets in app.py)
    model_name -> the Groq model to use, e.g. "groq/openai/gpt-oss-120b"
    """

    # 1. Connect CrewAI to Groq's LLM.
    # CrewAI understands the "groq/<model-id>" format out of the box.
    llm = LLM(
        model=model_name,
        api_key=api_key,
        temperature=0.3,   # low temperature = more focused, less "creative" output
    )

    # 2. Define the single agent that will do the review.
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
              ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
        cache=False,
    )

    # 3. Define the one task this agent must complete.
    # {resume_text} and {job_description} are placeholders that CrewAI fills
    # in automatically from the `inputs` dictionary passed to crew.kickoff().
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
            "2. List the candidate's strongest matching qualifications (skills, "
            "experience, achievements) that directly align with the job "
            "description.\n"
            "3. List important job requirements that are missing or only "
            "weakly represented in the resume.\n"
            "4. Give 5-8 concrete, actionable recommendations to improve the "
            "resume for this specific job. Each one should say what to change "
            "and why. Never suggest adding anything that isn't true — only "
            "suggest rewording, reordering, quantifying achievements, better "
            "highlighting things that are already there, or honestly learning "
            "a genuinely missing skill.\n"
            "5. Suggest 8-12 keywords taken from the job description that the "
            "candidate should naturally work into the resume (only where "
            "truthful), to help pass Applicant Tracking Systems (ATS).\n\n"
            "Format the entire answer in clean Markdown using exactly these "
            "section headers, in this order:\n"
            "## Match Score\n"
            "## Matching Strengths\n"
            "## Gaps & Missing Requirements\n"
            "## Actionable Recommendations\n"
            "## ATS Keywords to Add"
        ),
        expected_output=(
            "A well-formatted Markdown report with the five sections listed "
            "above, grounded only in the actual resume text provided, with no "
            "invented qualifications."
        ),
        agent=resume_reviewer,
    )

    # 4. Wrap the agent + task into a Crew. Sequential process = just run the
    # one task, in order (this is the simplest possible CrewAI setup).
    crew = Crew(
        agents=[resume_reviewer],
        tasks=[review_task],
        process=Process.sequential,
        verbose=False,
    )
    return crew


def run_resume_review(api_key: str, resume_text: str, job_description: str, model_name: str) -> str:
    """
    Convenience function used by app.py.
    Builds the crew, runs it with the given resume + job description, and
    returns the final Markdown report as plain text.
    """
    crew = build_crew(api_key=api_key, model_name=model_name)
    result = crew.kickoff(
        inputs={
            "resume_text": resume_text,
            "job_description": job_description,
        }
    )
    # CrewOutput objects convert nicely to a plain string with str()
    return str(result)
