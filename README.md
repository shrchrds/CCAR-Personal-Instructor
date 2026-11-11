# CCAR Personal Instructor

A Python CLI tool and React web app to help students prepare for the **Claude Certified Architect Professional (CCAR)** certification. Load modular question banks, run practice episodes, simulate a timed exam, and track progress across modules.

## Features

- **Practice Mode** — Study module-by-module with instant feedback
- **Exam Simulation** — Timed 40-question exam (40 minutes, 70% pass threshold)
- **Review** — See missed questions and study weak areas
- **Progress Tracking** — Persistent progress saved to `progress.json`
- **Study Guide** — Overview of all 6 exam domains
- **Web UI** — React-based browser interface for on-the-go study

## Requirements

- **Python 3.10+** (standard library only — no external dependencies)
- **Node.js 18+** (for the React web app)

## Quick Start

### CLI (Terminal)

```bash
python -m instructor.instructor
```

### Web App

```bash
cd ui
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

## Project Structure

```
instructor/
  instructor.py          # Main module: QuestionBank, Exam, ProgressManager, CLI
  questions/             # JSON question banks (one file per module)
    module_01_claude_platform.json
    module_02_enterprise_integration.json
    module_03_responsible_ai.json
    module_04_stakeholder_engagement.json
    module_05_ci_cd_and_operational_patterns.json
ui/                      # React web app (Vite)
  src/
    App.jsx              # Dashboard, exam UI
    components/          # Quiz, Results, AnswerOption
    data.js              # Question loading utilities
episode*/                # Episode reference materials (PDFs, slides)
```

## Exam Domins

| Domain | Topics |
|---|---|
| 1. Claude Architecture Fundamentals | Models, API, pricing, context windows |
| 2. Prompt Engineering | System prompts, JSON schema, chaining, few-shot |
| 3. Agentic Patterns | Agentic loop, multi-agent, tool use |
| 4. RAG Architecture | Retrieval, vector DBs, chunking, hybrid search |
| 5. Evaluation & Quality | Golden datasets, grading, cost analysis |
| 6. Production Systems | CI/CD, hooks, security, scalability |

## Adding Questions

Add a new `module_XX_<topic>.json` file in `instructor/questions/`:

```json
{
  "module": "06",
  "title": "Production Systems",
  "questions": [
    {
      "id": "M06-Q01",
      "question": "Which hook runs before a deployment?",
      "options": {"A": "pre_deploy", "B": "post_deploy", "C": "on_failure", "D": "on_success"},
      "correct": 0,
      "explanation": "The pre_deploy hook runs before any deployment starts."
    }
  ]
}
```

## License

MIT
