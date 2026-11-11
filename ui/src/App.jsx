// Adapted from mitchgavan/react-multi-choice-quiz (MIT)
// https://github.com/mitchgavan/react-multi-choice-quiz

import { useState, useEffect } from "react";
import Quiz from "./components/Quiz";
import Results from "./components/Results";
import { loadModules, loadModule, loadAllQuestions } from "./data";
import "./App.css";

const PASS_THRESHOLD = 70; // 70% to pass

const LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H"];

/** Transform a question from JSON format (array options + numeric index) to UI format (object options + letter key). */
function normalise(q) {
  const opts = {};
  if (Array.isArray(q.options)) {
    q.options.forEach((text, i) => {
      opts[LETTERS[i]] = text;
    });
    return { ...q, options: opts, correct: LETTERS[q.correct] };
  }
  return q; // already normalised
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    a[i] = a[j];
  }
  return a;
}

/* ---------- Dashboard View ---------- */
function Dashboard({ onPractice, onExam }) {
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModules().then((m) => {
      setModules(m);
      setLoading(false);
    });
  }, []);

  return (
    <div className="app-dashboard">
      <header className="app-header">
        <h1>CCAR Personal Instructor</h1>
        <p className="subtitle">Claude Certified Architect Professional</p>
      </header>

      <div className="menu-bar">
        <button className="menu-btn exam" onClick={onExam}>
          Simulated Exam (40 Q)
        </button>
      </div>

      <h2>Practice by Episode</h2>
      {loading ? (
        <p className="loading">Loading modules...</p>
      ) : modules.length === 0 ? (
        <p className="no-data">No modules found. Place JSON files in public/data/.</p>
      ) : (
        <div className="module-grid">
          {modules.map((mod) => (
            <button
              key={mod.id}
              className="module-card"
              onClick={() => onPractice(mod.id)}
            >
              <span className="module-number">EP {mod.number}</span>
              <span className="module-title">{mod.title}</span>
              <span className="module-count">{mod.questionCount} questions</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/* ---------- Main App ---------- */
function App() {
  // views: 'dashboard' | 'practice' | 'exam' | 'results'
  const [view, setView] = useState("dashboard");
  const [questions, setQuestions] = useState([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [selected, setSelected] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [mode, setMode] = useState("practice"); // "practice" | "exam"

  const startPractice = async (epNum) => {
    const mod = await loadModule(epNum);
    if (!mod) return;
    setMode("practice");
    setQuestions(shuffle(mod.questions).map(normalise));
    setAnswers([]);
    setCurrentQ(0);
    setSelected(null);
    setShowFeedback(false);
    setView("practice");
  };

  const startExam = async () => {
    const all = await loadAllQuestions();
    const picked = shuffle(all).slice(0, 40).map(normalise);
    setMode("exam");
    setQuestions(picked);
    setAnswers([]);
    setCurrentQ(0);
    setSelected(null);
    setShowFeedback(false);
    setView("exam");
  };

  const selectAnswer = (optKey) => {
    if (selected !== null && mode === "practice") return; // one pick in practice; exam allows changes
    setSelected(optKey);
    if (mode === "practice") {
      setShowFeedback(true);
    }
  };

  const goNext = () => {
    const correctKey = questions[currentQ].correct;
    setAnswers((prev) => [...prev, selected]);
    if (currentQ + 1 >= questions.length) {
      setView("results");
      return;
    }
    setCurrentQ((c) => c + 1);
    setSelected(null);
    setShowFeedback(false);
  };

  const goPrev = () => {
    if (currentQ <= 0) return;
    setCurrentQ((c) => c - 1);
    if (mode === "practice") {
      setSelected(null);
      setShowFeedback(false);
    } else {
      setSelected(answers[currentQ - 1] ?? null);
      setShowFeedback(false);
    }
  };

  const finishExam = () => {
    setView("results");
  };

  const goHome = () => {
    setView("dashboard");
    setQuestions([]);
    setAnswers([]);
    setCurrentQ(0);
    setSelected(null);
    setShowFeedback(false);
  };

  /* --- Results view --- */
  if (view === "results") {
    return (
      <Results
        questions={questions}
        answers={answers}
        mode={mode}
        passThreshold={PASS_THRESHOLD}
        onHome={goHome}
      />
    );
  }

  /* --- Practice / Exam view --- */
  if ((view === "practice" || view === "exam") && questions.length) {
    const q = questions[currentQ];
    return (
      <Quiz
        question={q}
        questionNum={currentQ + 1}
        total={questions.length}
        selected={selected}
        onSelect={selectAnswer}
        onNext={goNext}
        onPrev={goPrev}
        onHome={goHome}
        onFinish={finishExam}
        showFeedback={showFeedback}
        mode={mode}
      />
    );
  }

  /* --- Dashboard --- */
  return (
    <Dashboard onPractice={startPractice} onExam={startExam} />
  );
}

export default App;
