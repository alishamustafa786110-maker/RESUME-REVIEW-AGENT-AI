# 📄 AI Resume Review Agent

A beginner-friendly, single-agent app that reads a resume and a job
description, then tells you honestly how well they match and how to improve
the resume — built with **CrewAI**, **Groq**, and **Streamlit**.

The AI agent is instructed never to invent skills or experience that aren't
actually in your resume. It only works with what's really there.

---

## How it works (plain English)

1. You paste your resume text (or upload a PDF) and paste a job description.
2. The app extracts plain text from the PDF if needed.
3. A single AI "agent" (powered by an LLM running on Groq) reads both and
   compares them, acting like an experienced recruiter.
4. It returns a structured report: a match score, your strengths, the gaps,
   concrete fixes, and keywords to add — all grounded in your actual resume.

---

## File structure

```
resume-review-agent/
├── app.py                          # Streamlit user interface
├── crew_agent.py                   # The CrewAI agent, task, and crew logic
├── requirements.txt                # Python packages needed
├── .gitignore                      # Keeps secrets out of GitHub
├── .streamlit/
│   └── secrets.toml.example        # Template for your API key (safe to commit)
└── README.md                       # This file
```

Only **two Python files** do all the work: `app.py` (what the user sees) and
`crew_agent.py` (the AI logic). This keeps things easy to read and easy to
upload to GitHub.

---

## Step 1 — Get a free Groq API key

1. Go to https://console.groq.com and sign up (it's free to start).
2. Click **API Keys** in the left sidebar, then **Create API Key**.
3. Copy the key somewhere safe — you'll paste it in Step 3. You won't be able
   to see it again after you close that screen.

---

## Step 2 — Get the code onto your computer

1. Download or copy all the files in this project into a folder called
   `resume-review-agent`.
2. Open a terminal in that folder.

---

## Step 3 — Run it locally (optional, but good for testing)

1. Create the secrets file:
   - Copy `.streamlit/secrets.toml.example` to a new file at
     `.streamlit/secrets.toml`.
   - Open it and replace `your-groq-api-key-here` with your real Groq key.
   - **Never commit this real file to GitHub** — the `.gitignore` file
     already prevents this by accident.

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:
   ```bash
   streamlit run app.py
   ```

4. Your browser should open automatically at `http://localhost:8501`. If not,
   copy the local URL shown in your terminal into your browser.

---

## Step 4 — Put the code on GitHub

1. Create a new (empty) repository on GitHub — do **not** add a README there
   (you already have one).
2. In your project folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI Resume Review Agent"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
3. Double-check on GitHub.com that `.streamlit/secrets.toml` (the real one
   with your key) is **not** in the repository — only
   `secrets.toml.example` should be there.

---

## Step 5 — Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **Create app** → **From existing repo**.
3. Select your `resume-review-agent` repository and the `main` branch.
4. Set the main file path to `app.py`.
5. Under **Advanced settings → Secrets**, paste in:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
   (Use your real key here — this box is private and separate from GitHub.)
6. Choose **Python version 3.11** in the advanced settings if asked.
7. Click **Deploy**. After a minute or two, your app will be live at a public
   URL you can share.

---

## What happens if something goes wrong?

The app is built to fail gracefully instead of crashing:

| Situation | What the app does |
|---|---|
| No Groq API key set | Shows a clear setup message and stops, instead of erroring out |
| Resume or job description left empty | Shows a friendly reminder to fill it in |
| PDF can't be read (scanned image, corrupted, locked) | Warns you and suggests pasting text instead |
| Groq rate limit hit | Tells you to wait a bit and try again |
| Groq API key invalid/expired | Tells you to check your key |
| Network/timeout issue | Tells you to retry |

---

## Customizing

- **Change the model:** edit `MODEL_NAME` at the top of `app.py`. Any valid
  Groq production model works, using the format `"groq/<model-id>"`
  (e.g. `"groq/llama-3.3-70b-versatile"`).
- **Change what the agent focuses on:** edit the `description` text inside
  `build_crew()` in `crew_agent.py`. This is the actual instruction the AI
  agent follows.
- **Add more sections to the report:** add them to the task description and
  to the list of Markdown headers.

---

## Why this counts as a "CrewAI agent" app

Even though there's only one agent, this uses the real CrewAI building
blocks: an `Agent` (with a role, goal, and backstory), a `Task` (the specific
job to do), and a `Crew` (which runs the agent through the task). This is
the simplest possible CrewAI setup, and a great starting point before adding
more agents (e.g. a separate "cover letter writer" agent) later.
