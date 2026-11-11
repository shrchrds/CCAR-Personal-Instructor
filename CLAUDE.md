# CLAUDE.md — Project Conventions

## Project: CCAR Personal Instructor

A Python CLI tool to help students prepare for the **Claude Certified Architect Professional (CCAR)** certification. It loads modular JSON question banks, runs practice episodes, simulates a timed exam, and tracks progress.

## Tech Stack

- **Language:** Python 3.10+ (standard library only — no external dependencies)
- **Structure:** `instructor/` is a Python package; the CLI entry point is `python -m instructor.instructor`
- **Data:** JSON question banks in `instructor/questions/` — one file per module (`module_XX_<topic>.json`)

## File Layout

```
instructor/
  __init__.py
  instructor.py          # Main module: QuestionBank, Exam, ProgressManager, CLI
  questions/
    module_01_claude_platform.json
    module_02_enterprise_integration.json
    module_03_responsible_ai.json
    module_04_stakeholder_engagement.json
    module_05_ci_cd_and_operational_patterns.json
CLAUDE.md                # This file
```

## Key Conventions

### File Operations
- **One file per edit:** To avoid truncation, change only ONE file per step.
- No large multi-file rewrites. Use `edit_file` or `multi_edit` for incremental changes.

### Encoding
- **ASCII only.** No Unicode box-drawing chars, emoji, or special symbols.
- Use ASCII equivalents: `+` for corners, `-` for lines, `#` for blocks, `*` for bullets, `x` for errors, `+` for checks.
- All print output must work on Windows cp1252.

### Passing Threshold
- `PASS_THRESHOLD = 28` (70% of 40 questions)
- `TOTAL_QUESTIONS = 40` for exam simulation

### Question Bank Format
Each `module_XX_<topic>.json` contains:
```json
{
  "module": "01",
  "title": "Module Title",
  "questions": [
    {
      "id": "M01-Q01",
      "question": "Question text?",
      "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
      "answer": "A",
      "explanation": "Why A is correct.",
      "difficulty": "basic"
    }
  ]
}
```

- `module` is a 2-digit number (01-05) matching the filename prefix.
- `difficulty` values: `basic`, `intermediate`, `advanced`.
- `id` format: `M{XX}-Q{NN}`.

### Progress Tracking
- Progress saved to `instructor/progress.json` — auto-created on first run.
- Stores completion status, scores, and timestamps per module.

### Entry Point
```bash
python -m instructor.instructor
```
- Do NOT run `python instructor/instructor.py` (breaks `__name__ == "__main__"`).
- No `app.py` or `main.py` — the module IS the entry point.

### Adding Content
1. Add a new `module_XX_<topic>.json` to `instructor/questions/`
2. Follow the JSON schema above
3. Ensure the module number is unique and sequential

### Dependencies
- None. Standard library only.

## Testing

- No test framework installed. Quick smoke test:
  ```bash
  python -c "from instructor.instructor import QuestionBank; qb = QuestionBank(); print(len(qb.banks), 'modules loaded')"
  ```
