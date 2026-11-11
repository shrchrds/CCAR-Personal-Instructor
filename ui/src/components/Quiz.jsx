// Adapted from mitchgavan/react-multi-choice-quiz (MIT)
// https://github.com/mitchgavan/react-multi-choice-quiz
// Components: Question, QuestionCount, AnswerOption merged into one functional quiz.

import AnswerOption from "./AnswerOption";

function Quiz({
  question,
  questionNum,
  total,
  selected,
  onSelect,
  onNext,
  onPrev,
  onHome,
  onFinish,
  showFeedback,
  mode, // "practice" | "exam"
}) {
  const correctKey = question.correct;
  const isLast = questionNum === total;

  return (
    <div className="app-quiz">
      <header className="quiz-header">
        <button className="btn-home" onClick={onHome}>
          + Back to Dashboard
        </button>
        <div className="question-count">
          Question <span>{questionNum}</span> of <span>{total}</span>
        </div>
        {mode === "practice" && (
          <div className={`feedback-badge ${selected === correctKey ? "correct" : "incorrect"}`}>
            {selected === null ? "" : selected === correctKey ? "Correct" : "Incorrect"}
          </div>
        )}
      </header>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${(questionNum / total) * 100}%` }}
        />
      </div>

      <main className="quiz-body">
        <h2 className="question">{question.question}</h2>

        <div className="options">
          {Object.entries(question.options).map(([key, text]) => (
            <AnswerOption
              key={key}
              value={key}
              content={text}
              isSelected={selected === key}
              isCorrect={key === correctKey}
              showFeedback={showFeedback}
              mode={mode}
              onSelect={onSelect}
            />
          ))}
        </div>

        {showFeedback && question.explanation && (
          <div className="explanation">
            <strong>Explanation:</strong> {question.explanation}
          </div>
        )}
      </main>

      <footer className="quiz-footer">
        <button
          className="btn-nav"
          disabled={questionNum === 1}
          onClick={onPrev}
        >
          Previous
        </button>

        {mode === "exam" ? (
          isLast ? (
            <button className="btn-submit" onClick={onFinish}>
              Submit Exam
            </button>
          ) : (
            <button className="btn-submit" onClick={onNext}>
              Next
            </button>
          )
        ) : (
          <button className="btn-submit" onClick={onNext}>
            {isLast ? "Finish" : "Next"}
          </button>
        )}
      </footer>
    </div>
  );
}

export default Quiz;
