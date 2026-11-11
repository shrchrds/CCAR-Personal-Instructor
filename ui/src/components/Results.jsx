// Adapted from mitchgavan/react-multi-choice-quiz (MIT)
// https://github.com/mitchgavan/react-multi-choice-quiz

import { useState } from "react";

function Results({ questions, answers, mode, passThreshold, onHome }) {
  const [reviewIndex, setReviewIndex] = useState(0);

  const total = questions.length;
  const correctCount = questions.reduce((sum, q, i) => {
    return sum + (answers[i] === q.correct ? 1 : 0);
  }, 0);
  const pct = Math.round((correctCount / total) * 100);
  const passed = pct >= passThreshold;

  const q = questions[reviewIndex];
  const a = answers[reviewIndex];

  return (
    <div className="app-results">
      <header className="results-header">
        <h1>{mode === "exam" ? "Exam Results" : "Practice Results"}</h1>
      </header>

      <div className={`score-card ${passed ? "pass" : "fail"}`}>
        <div className="score-pct">{pct}%</div>
        <div className="score-label">{passed ? "PASSED" : "NEEDS MORE PRACTICE"}</div>
        <div className="score-detail">
          {correctCount} of {total} correct
        </div>
      </div>

      <div className="review-section">
        <h2>Review Questions</h2>

        <div className="review-card">
          <div className="review-qnum">
            Question {reviewIndex + 1} of {total}
          </div>
          <p className="review-question">{q.question}</p>
          <div className="review-answer">
            <span className="your-answer">
              Your answer: <strong>{a ?? "none"}</strong>
              {a === q.correct ? " [ok]" : a !== null ? " [x]" : ""}
            </span>
            <span className="correct-answer">
              Correct: <strong>{q.correct}</strong>
            </span>
          </div>
          {q.explanation && (
            <div className="review-explanation">{q.explanation}</div>
          )}
        </div>

        <div className="review-nav">
          <button
            className="btn-nav"
            disabled={reviewIndex === 0}
            onClick={() => setReviewIndex((i) => i - 1)}
          >
            Previous
          </button>
          <button
            className="btn-nav"
            disabled={reviewIndex === total - 1}
            onClick={() => setReviewIndex((i) => i + 1)}
          >
            Next
          </button>
        </div>
      </div>

      <button className="btn-home big" onClick={onHome}>
        Back to Dashboard
      </button>
    </div>
  );
}

export default Results;
