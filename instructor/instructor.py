#!/usr/bin/env python3
"""
CCAR Personal Instructor - Core Engine
Claude Certified Architect Professional Certification

Modes:
  practice  - Answer questions for a specific episode
  exam      - Simulated certification exam (40 random questions, 40 min)
  review    - Review your previously missed questions
  progress  - Show your progress across all episodes

Usage:
  python instructor.py practice <episode_number>
  python instructor.py exam
  python instructor.py review
  python instructor.py progress
"""

import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

# -- Paths --------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
QUESTIONS_DIR = BASE_DIR / "questions"
PROGRESS_FILE = BASE_DIR / "progress.json"

# -- ANSI Colors --------------------------------------------------------------
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"

# Disable colors on Windows if needed
if sys.platform == "win32":
    import ctypes
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        C.RESET = C.BOLD = C.DIM = C.GREEN = C.RED = C.YELLOW = C.BLUE = C.CYAN = C.MAGENTA = ""

# -- Progress Manager ---------------------------------------------------------
class ProgressManager:
    """Tracks user progress, scores, and missed questions."""

    def __init__(self):
        self.data = self._load()

    def _load(self):
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        return {
            "episodes": {},
            "exam_attempts": [],
            "last_review": None,
            "total_correct": 0,
            "total_attempted": 0,
            "missed_questions": []  # list of {"episode": N, "q_index": I}
        }

    def save(self):
        with open(PROGRESS_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def record_answer(self, episode, q_index, correct, explanation=""):
        if "episodes" not in self.data:
            self.data["episodes"] = {}
        ep_key = str(episode)
        if ep_key not in self.data["episodes"]:
            self.data["episodes"][ep_key] = {"correct": 0, "attempted": 0, "missed": []}
        self.data["episodes"][ep_key]["attempted"] += 1
        self.data["total_attempted"] += 1
        if correct:
            self.data["episodes"][ep_key]["correct"] += 1
            self.data["total_correct"] += 1
            # Remove from missed if was there
            self.data["missed_questions"] = [
                m for m in self.data["missed_questions"]
                if not (m.get("episode") == episode and m.get("q_index") == q_index)
            ]
        else:
            self.data["episodes"][ep_key]["missed"].append(q_index)
            # Add to missed if not already there
            existing = any(
                m.get("episode") == episode and m.get("q_index") == q_index
                for m in self.data["missed_questions"]
            )
            if not existing:
                self.data["missed_questions"].append({"episode": episode, "q_index": q_index})
        self.save()

    def get_episode_score(self, episode):
        ep_key = str(episode)
        ep = self.data.get("episodes", {}).get(ep_key)
        if not ep or ep["attempted"] == 0:
            return None
        return round(ep["correct"] / ep["attempted"] * 100, 1)

    def get_all_missed(self):
        return self.data.get("missed_questions", [])

    def record_exam_attempt(self, score, total, time_used):
        self.data["exam_attempts"].append({
            "date": datetime.now().isoformat(),
            "score": score,
            "total": total,
            "percentage": round(score / total * 100, 1),
            "time_minutes": round(time_used / 60, 1),
            "passed": score / total >= 0.7  # 70% pass threshold
        })
        self.save()


# -- Question Bank Loader -----------------------------------------------------
class QuestionBank:
    """Loads and serves questions from JSON files."""

    def __init__(self):
        self.banks = {}
        self._load_all()

    def _load_all(self):
        if not QUESTIONS_DIR.exists():
            return
        for qfile in QUESTIONS_DIR.glob("module_*.json"):
            ep_num = int(qfile.stem.split("_")[1])
            with open(qfile, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.banks[ep_num] = {
                "title": data.get("title", f"Episode {ep_num}"),
                "description": data.get("description", ""),
                "questions": data.get("questions", [])
            }

    def get_episode(self, episode):
        return self.banks.get(episode)

    def get_all_episodes(self):
        return sorted(self.banks.keys())

    def get_random_questions(self, count=40):
        all_q = []
        for ep_num, bank in self.banks.items():
            for i, q in enumerate(bank["questions"]):
                all_q.append({"episode": ep_num, "index": i, "question": q})
        random.shuffle(all_q)
        return all_q[:count]


# -- Terminal Helpers ----------------------------------------------------------
def clear_screen():
    # ANSI escape: clear screen + move cursor to top-left. No shell needed.
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def pause():
    input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")

def print_banner():
    print(f"""
{C.CYAN}{C.BOLD}
+-------------------------------------------------------------------+
|                                                                   |
|          CCAR PERSONAL INSTRUCTOR                                |
|     Claude Certified Architect Professional                       |
|                                                                   |
|   Your AI-powered path to certification                           |
|                                                                   |
+-------------------------------------------------------------------+
{C.RESET}
""")

def print_menu():
    print(f"""
{C.BOLD}-- MAIN MENU --{C.RESET}

  {C.GREEN}1{C.RESET}. {C.BOLD}Practice by Episode{C.RESET}   - Study one episode at a time
  {C.GREEN}2{C.RESET}. {C.BOLD}Simulated Exam{C.RESET}        - Full certification exam (40 Q, 40 min)
  {C.GREEN}3{C.RESET}. {C.BOLD}Review Missed{C.RESET}         - Practice questions you got wrong
  {C.GREEN}4{C.RESET}. {C.BOLD}Progress Report{C.RESET}       - See how you're doing
  {C.GREEN}5{C.RESET}. {C.BOLD}Study Guide{C.RESET}           - Key topics and concepts
  {C.GREEN}0{C.RESET}. {C.RED}Exit{C.RESET}

""")

# -- Practice Mode -------------------------------------------------------------
def run_practice(qb, pm):
    episodes = qb.get_all_episodes()
    if not episodes:
        print(f"\n{C.RED}No question banks found.{C.RESET}")
        return

    print(f"\n{C.BOLD}-- PRACTICE MODE --{C.RESET}\n")
    for ep in episodes:
        bank = qb.get_episode(ep)
        score = pm.get_episode_score(ep)
        status = f"{C.GREEN}+ {score}%{C.RESET}" if score else f"{C.DIM}not started{C.RESET}"
        print(f"  {C.CYAN}{ep:2d}{C.RESET}. {bank['title']}  ({len(bank['questions'])} Q) {status}")
    print()

    try:
        choice = input(f"{C.BOLD}Select episode (0-{max(episodes)}), or 'b' to go back: {C.RESET}")
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if choice.lower() in ("b", "q", "0"):
        return

    try:
        ep_num = int(choice)
    except ValueError:
        print(f"\n{C.RED}Invalid selection.{C.RESET}")
        return

    bank = qb.get_episode(ep_num)
    if not bank:
        print(f"\n{C.RED}Episode {ep_num} not found.{C.RESET}")
        return

    print(f"\n{C.BOLD}-- Episode {ep_num}: {bank['title']} --{C.RESET}")
    if bank["description"]:
        print(f"{C.DIM}{bank['description']}{C.RESET}")
    print(f"{C.DIM}{len(bank['questions'])} questions{C.RESET}\n")

    score = 0
    for i, q in enumerate(bank["questions"]):
        print(f"  {C.BOLD}Q{i+1}/{len(bank['questions'])}{C.RESET}  {C.CYAN}{q['question']}{C.RESET}\n")

        options = q["options"]
        for j, opt in enumerate(options):
            print(f"    {chr(65+j)}) {opt}")
        print()

        try:
            ans = input(f"  Your answer ({'-'.join(chr(65+j) for j in range(len(options)))}): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        correct_idx = q["correct"]
        correct_char = chr(65 + correct_idx)

        if ans == correct_char:
            print(f"  {C.GREEN}+ Correct!{C.RESET}")
            score += 1
            pm.record_answer(ep_num, i, True)
        else:
            print(f"  {C.RED}x Incorrect.{C.RESET}")
            print(f"  {C.GREEN}Correct: {correct_char}) {options[correct_idx]}{C.RESET}")
            pm.record_answer(ep_num, i, False)

        if "explanation" in q and q["explanation"]:
            print(f"  {C.YELLOW} {q['explanation']}{C.RESET}")
        pause()

    percentage = round(score / len(bank["questions"]) * 100, 1) if bank["questions"] else 0
    print(f"\n{C.BOLD}-- Episode {ep_num} Results --{C.RESET}")
    print(f"  {C.CYAN}Score:{C.RESET} {score}/{len(bank['questions'])} ({percentage}%)")
    if percentage >= 80:
        print(f"  {C.GREEN}Excellent! Ready for exam mode.{C.RESET}")
    elif percentage >= 60:
        print(f"  {C.YELLOW}Good progress. Review missed questions.{C.RESET}")
    else:
        print(f"  {C.RED}Keep studying. Review the episode material and try again.{C.RESET}")


# -- Exam Mode -----------------------------------------------------------------
def run_exam(qb, pm):
    all_q = qb.get_random_questions(40)
    if not all_q:
        print(f"\n{C.RED}Not enough questions for an exam.{C.RESET}")
        return

    print(f"\n{C.BOLD}-- SIMULATED CCAR EXAM --{C.RESET}")
    print(f"{C.YELLOW}40 questions * 40 minutes * 70% to pass{C.RESET}")
    print(f"{C.DIM}Questions are randomized from all episodes.{C.RESET}\n")

    try:
        confirm = input("Start the exam? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if confirm != "y":
        return

    clear_screen()
    print(f"{C.BOLD}-- EXAM STARTED --{C.RESET}")
    print(f"Time limit: 40 minutes\n")
    start_time = time.time()

    score = 0
    for i, q_data in enumerate(all_q):
        elapsed = time.time() - start_time
        remaining = max(0, 40 * 60 - elapsed)
        mins = int(remaining // 60)
        secs = int(remaining % 60)

        q = q_data["question"]
        print(f"  {C.BOLD}Q{i+1}/40{C.RESET}  [Time: {mins:02d}:{secs:02d} remaining]")
        print(f"  {C.CYAN}[Episode {q_data['episode']}] {q['question']}{C.RESET}\n")

        options = q["options"]
        for j, opt in enumerate(options):
            print(f"    {chr(65+j)}) {opt}")
        print()

        try:
            ans = input(f"  Your answer ({'-'.join(chr(65+j) for j in range(len(options)))}): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\nExam interrupted.")
            break

        correct_idx = q["correct"]

        if ans == chr(65 + correct_idx):
            print(f"  {C.GREEN}+ Correct!{C.RESET}")
            score += 1
        else:
            print(f"  {C.RED}x Incorrect.{C.RESET}")
            print(f"  {C.GREEN}Correct: {chr(65 + correct_idx)}) {options[correct_idx]}{C.RESET}")

        if "explanation" in q and q["explanation"]:
            print(f"  {C.YELLOW} {q['explanation']}{C.RESET}")

        # Record for progress
        pm.record_answer(q_data["episode"], q_data["index"], ans == chr(65 + correct_idx))

    time_used = time.time() - start_time
    percentage = round(score / len(all_q) * 100, 1)

    pm.record_exam_attempt(score, len(all_q), time_used)

    clear_screen()
    print(f"{C.BOLD}-- EXAM RESULTS --{C.RESET}\n")
    print(f"  {C.CYAN}Score:{C.RESET}     {score}/{len(all_q)} ({percentage}%)")
    print(f"  {C.CYAN}Time used:{C.RESET} {int(time_used//60)}m {int(time_used%60)}s")

    if percentage >= 70:
        print(f"\n  {C.GREEN} PASSED! You scored above the 70% threshold.{C.RESET}")
    else:
        print(f"\n  {C.RED}x Did not pass. You need 70% to pass.{C.RESET}")
        missed = pm.get_all_missed()
        if missed:
            print(f"  {C.YELLOW}Review your {len(missed)} missed questions in Review mode.{C.RESET}")


# -- Review Mode ---------------------------------------------------------------
def run_review(qb, pm):
    missed = pm.get_all_missed()
    if not missed:
        print(f"\n{C.GREEN}No missed questions to review! Keep up the great work.{C.RESET}")
        return

    print(f"\n{C.BOLD}-- REVIEW MODE --{C.RESET}")
    print(f"{C.YELLOW}{len(missed)} missed questions to review{C.RESET}\n")

    score = 0
    for m in missed:
        ep_num = m["episode"]
        q_index = m["q_index"]
        bank = qb.get_episode(ep_num)
        if not bank or q_index >= len(bank["questions"]):
            continue

        q = bank["questions"][q_index]
        print(f"  {C.CYAN}[Episode {ep_num}] {q['question']}{C.RESET}\n")

        options = q["options"]
        for j, opt in enumerate(options):
            print(f"    {chr(65+j)}) {opt}")
        print()

        try:
            ans = input(f"  Your answer ({'-'.join(chr(65+j) for j in range(len(options)))}): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        correct_idx = q["correct"]

        if ans == chr(65 + correct_idx):
            print(f"  {C.GREEN}+ Got it right this time!{C.RESET}")
            score += 1
            pm.record_answer(ep_num, q_index, True)
        else:
            print(f"  {C.RED}x Still incorrect.{C.RESET}")
            print(f"  {C.GREEN}Correct: {chr(65 + correct_idx)}) {options[correct_idx]}{C.RESET}")

        if "explanation" in q and q["explanation"]:
            print(f"  {C.YELLOW} {q['explanation']}{C.RESET}")
        pause()

    print(f"\n{C.BOLD}Review Score: {score}/{len(missed)}{C.RESET}")


# -- Progress Report -----------------------------------------------------------
def run_progress(qb, pm):
    print(f"\n{C.BOLD}-- PROGRESS REPORT --{C.RESET}\n")

    total_correct = pm.data.get("total_correct", 0)
    total_attempted = pm.data.get("total_attempted", 0)

    if total_attempted > 0:
        overall = round(total_correct / total_attempted * 100, 1)
        print(f"  {C.BOLD}Overall Accuracy:{C.RESET} {total_correct}/{total_attempted} ({overall}%)")
    else:
        print(f"  {C.DIM}No questions attempted yet.{C.RESET}")

    print()
    episodes = qb.get_all_episodes()
    for ep in episodes:
        bank = qb.get_episode(ep)
        ep_data = pm.data.get("episodes", {}).get(str(ep), {"correct": 0, "attempted": 0})
        attempted = ep_data.get("attempted", 0)
        correct = ep_data.get("correct", 0)

        if attempted > 0:
            pct = round(correct / attempted * 100, 1)
            bar_len = 20
            filled = int(bar_len * correct / attempted)
            bar = f"[{C.GREEN}{'-'*filled}{C.RED}{'-'*(bar_len-filled)}{C.RESET}]"
            print(f"  Ep {ep:2d} {bank['title'][:35]:<35} {bar} {pct}%")
        else:
            print(f"  Ep {ep:2d} {bank['title'][:35]:<35} {'[-' + '-'*(19) + ']' :24}  0%")

    # Exam history
    exams = pm.data.get("exam_attempts", [])
    if exams:
        print(f"\n  {C.BOLD}Exam History:{C.RESET}")
        for i, ex in enumerate(exams[-5:], 1):
            status = f"{C.GREEN}PASS{C.RESET}" if ex["passed"] else f"{C.RED}FAIL{C.RESET}"
            print(f"    Attempt {i}: {ex['percentage']}% {status} ({ex['time_minutes']}min) on {ex['date'][:10]}")

    missed = pm.get_all_missed()
    print(f"\n  {C.BOLD}Questions to review:{C.RESET} {len(missed)}")


# -- Study Guide ---------------------------------------------------------------
def run_study_guide():
    print(f"""
{C.BOLD}-- CCAR STUDY GUIDE --{C.RESET}

{C.CYAN}Domain 1: Claude Architecture Fundamentals{C.RESET}
  * What is Claude? Models, capabilities, use cases
  * Model selection (Sonnet, Opus, Haiku)
  * API basics and pricing
  * Context windows, token limits

{C.CYAN}Domain 2: Prompt Engineering{C.RESET}
  * System prompts and instruction design
  * Structured output (JSON schema)
  * Prompt chaining and composition
  * Few-shot prompting

{C.CYAN}Domain 3: Agentic Patterns{C.RESET}
  * The agentic loop (plan -> act -> observe -> reflect)
  * Hub-and-spoke architecture
  * Multi-agent systems
  * Tool use and function calling

{C.CYAN}Domain 4: RAG Architecture{C.RESET}
  * Retrieval-Augmented Generation
  * Vector databases and embeddings
  * Chunking strategies
  * Hybrid search

{C.CYAN}Domain 5: Evaluation & Quality{C.RESET}
  * Building evaluation frameworks
  * Golden datasets and grading
  * Cost analysis and optimization
  * Production monitoring

{C.CYAN}Domain 6: Production Systems{C.RESET}
  * Claude Code and CI/CD
  * Hooks and lifecycle management
  * Security and guardrails
  * Scalability patterns

{C.DIM}Pass threshold: 70% (28/40 correct){C.RESET}
{C.DIM}Exam format: 40 questions, 40 minutes{C.RESET}
""")


# -- Main ----------------------------------------------------------------------
def main():
    qb = QuestionBank()
    pm = ProgressManager()

    while True:
        clear_screen()
        print_banner()
        print_menu()

        try:
            choice = input(f"{C.BOLD}Select an option: {C.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.CYAN}Goodbye! Keep studying!{C.RESET}")
            break

        if choice == "1":
            run_practice(qb, pm)
            pause()
        elif choice == "2":
            run_exam(qb, pm)
            pause()
        elif choice == "3":
            run_review(qb, pm)
            pause()
        elif choice == "4":
            run_progress(qb, pm)
            pause()
        elif choice == "5":
            run_study_guide()
            pause()
        elif choice == "0":
            print(f"\n{C.CYAN}Goodbye! Keep studying!{C.RESET}")
            break
        else:
            print(f"\n{C.RED}Invalid option.{C.RESET}")
            pause()


if __name__ == "__main__":
    main()