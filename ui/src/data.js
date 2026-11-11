// Adapted from mitchgavan/react-multi-choice-quiz (MIT)
// https://github.com/mitchgavan/react-multi-choice-quiz

/** Fetch all module data files and return an array of module summaries. */
async function loadModules() {
  const modules = [];
  let ep = 1;
  while (ep <= 20) {
    const path = `data/module_${String(ep).padStart(2, "0")}_*.json`;
    try {
      /* We try known filenames built from the Python module numbering */
      const nameMap = {
        1: "claude_platform",
        2: "enterprise_integration",
        3: "responsible_ai",
        4: "stakeholder_engagement",
        5: "ci_cd_and_operational_patterns",
      };
      if (nameMap[ep]) {
        const res = await fetch(`/data/module_${String(ep).padStart(2, "0")}_${nameMap[ep]}.json`);
        if (res.ok) {
          const data = await res.json();
          modules.push({
            id: ep,
            number: ep,
            title: data.title || `Episode ${ep}`,
            description: data.description || "",
            questionCount: data.questions?.length || 0,
          });
        }
      }
    } catch {
      /* skip */
    }
    ep++;
  }
  return modules;
}

/** Load a single module's full question data. */
async function loadModule(epNum) {
  const nameMap = {
    1: "claude_platform",
    2: "enterprise_integration",
    3: "responsible_ai",
    4: "stakeholder_engagement",
    5: "ci_cd_and_operational_patterns",
  };
  const name = nameMap[epNum];
  if (!name) return null;
  const res = await fetch(`/data/module_${String(epNum).padStart(2, "0")}_${name}.json`);
  if (!res.ok) return null;
  return res.json();
}

/** Load ALL questions from every module (for exam mode). */
async function loadAllQuestions() {
  const all = [];
  let ep = 1;
  while (ep <= 20) {
    try {
      const mod = await loadModule(ep);
      if (mod && mod.questions) {
        for (const q of mod.questions) {
          all.push({ ...q, module: ep, title: mod.title });
        }
      }
    } catch {
      /* skip */
    }
    ep++;
  }
  return all;
}

export { loadModules, loadModule, loadAllQuestions };
