// Adapted from mitchgavan/react-multi-choice-quiz (MIT)
// https://github.com/mitchgavan/react-multi-choice-quiz

import { useState } from "react";

function AnswerOption({
  value,
  content,
  isSelected,
  isCorrect,
  showFeedback,
  mode,
  onSelect,
}) {
  const [hovered, setHovered] = useState(false);

  let cls = "answer-option";
  if (hovered && !isSelected && !showFeedback) cls += " hover";
  if (isSelected) cls += " selected";
  if (showFeedback && isCorrect) cls += " correct";
  if (showFeedback && isSelected && !isCorrect) cls += " incorrect";
  if (mode === "exam") cls += " exam-mode";

  // Determine if clicks should be allowed
  const disabled =
    mode === "practice"
      ? showFeedback
      : false;

  return (
    <button
      className={cls}
      disabled={disabled}
      onClick={() => onSelect(value)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <span className="option-letter">{value}</span>
      <span className="option-text">{content}</span>
      {showFeedback && isCorrect && <span className="option-icon">[ok]</span>}
      {showFeedback && isSelected && !isCorrect && (
        <span className="option-icon">[x]</span>
      )}
    </button>
  );
}

export default AnswerOption;
