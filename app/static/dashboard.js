// ═══════════════════════════════════════════════════════════════════════════════
// dashboard.js — StudyMate AI authenticated-page interactions
// Aurelius Dark UI — full rewrite (Task 14)
// ═══════════════════════════════════════════════════════════════════════════════

// ── Auth helpers ──────────────────────────────────────────────────────────────
function getToken() {
  return localStorage.getItem("studymate-token");
}

function getUser() {
  const raw = localStorage.getItem("studymate-user");
  return raw ? JSON.parse(raw) : null;
}

// ── Request helper ────────────────────────────────────────────────────────────
async function requestJson(url, options = {}, useAuth = false) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (useAuth && getToken()) headers.Authorization = `Bearer ${getToken()}`;
  const response = await fetch(url, { ...options, headers });
  const raw = await response.text();
  let data = {};
  try { data = raw ? JSON.parse(raw) : {}; } catch { throw new Error(raw || "Unexpected server response."); }
  if (!response.ok) throw new Error(data.detail || "Request failed.");
  return data;
}

// ── UI helpers ────────────────────────────────────────────────────────────────
const feedback = document.getElementById("feedback");
const spinner  = document.getElementById("spinner");

function showFeedback(message, timeout = 2600) {
  if (!feedback) return;
  feedback.textContent = message;
  feedback.style.display = "";
  feedback.classList.remove("d-none");
  clearTimeout(showFeedback._timer);
  showFeedback._timer = setTimeout(() => {
    feedback.style.display = "none";
    feedback.classList.add("d-none");
  }, timeout);
}

function setLoading(isLoading, message = "Working on it…") {
  if (!spinner) return;
  spinner.style.display = isLoading ? "" : "none";
  spinner.hidden = !isLoading;
  spinner.classList.toggle("d-none", !isLoading);
  const statusEl = document.getElementById("spinnerStatus");
  if (statusEl) statusEl.textContent = message;
}

function animateBlock(el) {
  if (!el) return;
  el.classList.remove("fade-stack");
  requestAnimationFrame(() => el.classList.add("fade-stack"));
}

async function copyText(value, msg) {
  if (!value || !value.trim()) { showFeedback("Nothing to copy yet."); return; }
  try {
    await navigator.clipboard.writeText(value);
    showFeedback(msg || "Copied!");
  } catch {
    showFeedback("Copy failed on this browser.");
  }
}

// ── Auto-resize textarea ──────────────────────────────────────────────────────
function autoResize(el) {
  if (!el) return;
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 320) + "px";
}

// ── Metrics (word / char count) ───────────────────────────────────────────────
const noteText  = document.getElementById("noteText");
const wordCount = document.getElementById("wordCount");
const charCount = document.getElementById("charCount");

function updateMetrics() {
  if (!noteText) return;
  const text    = noteText.value;
  const trimmed = text.trim();
  if (charCount) charCount.textContent = text.length.toLocaleString();
  if (wordCount) wordCount.textContent = trimmed ? trimmed.split(/\s+/).length.toLocaleString() : "0";
}

if (noteText) {
  noteText.addEventListener("input", () => { autoResize(noteText); updateMetrics(); });
}

// ── Sidebar toggle ────────────────────────────────────────────────────────────
function toggleSidebar(forceOpen) {
  const shell = document.querySelector(".dashboard-shell");
  if (!shell) return;
  const open = typeof forceOpen === "boolean" ? forceOpen : !shell.classList.contains("sidebar-open");
  shell.classList.toggle("sidebar-open", open);
  const toggleBtn = document.querySelector("[data-sidebar-open]");
  if (toggleBtn) toggleBtn.setAttribute("aria-expanded", String(open));
}

document.querySelector("[data-sidebar-open]")?.addEventListener("click", () => toggleSidebar(true));
document.querySelectorAll("[data-sidebar-close]").forEach(btn =>
  btn.addEventListener("click", () => toggleSidebar(false))
);
window.addEventListener("resize", () => { if (window.innerWidth > 1199) toggleSidebar(false); });

// ── Auth state rendering ──────────────────────────────────────────────────────
const authState   = document.getElementById("authState");
const logoutBtn   = document.getElementById("logoutBtn");
const profileName  = document.getElementById("profileName");
const profileEmail = document.getElementById("profileEmail");
const profileAvatar = document.getElementById("profileAvatar");

function populateProfile() {
  const user = getUser();
  if (!user) return;
  if (profileName)  profileName.textContent  = user.name  || "StudyMate User";
  if (profileEmail) profileEmail.textContent = user.email || "Signed in";
  if (profileAvatar) {
    const src = user.name || user.email || "S";
    profileAvatar.textContent = src.trim().charAt(0).toUpperCase();
  }
  // sidebar user footer
  const sidebarName   = document.querySelector(".sidebar-user-name");
  const sidebarAvatar = document.querySelector(".sidebar-user-avatar");
  if (sidebarName)   sidebarName.textContent   = user.name  || "StudyMate User";
  if (sidebarAvatar) sidebarAvatar.textContent = (user.name || user.email || "S").trim().charAt(0).toUpperCase();
}

function updateAuthState() {
  if (!authState) return;
  const user = getUser();
  if (!user) {
    if (authState) authState.textContent = "Guest mode";
    if (logoutBtn) { logoutBtn.style.display = "none"; logoutBtn.classList.add("d-none"); }
    return;
  }
  if (authState) authState.textContent = user.name || "Account";
  if (logoutBtn) { logoutBtn.style.display = ""; logoutBtn.classList.remove("d-none"); }
}

logoutBtn?.addEventListener("click", () => {
  localStorage.removeItem("studymate-token");
  localStorage.removeItem("studymate-user");
  window.location.href = "/";
});

// ── State ─────────────────────────────────────────────────────────────────────
let currentLevel            = "basic";
let currentSummary          = [];
let currentExplanation      = [];
let currentQuiz             = [];
let currentSlides           = [];
let currentUploadedFileName = "";
let summaryRating           = null;
let explanationRating       = null;

const noteTitle      = document.getElementById("noteTitle");
const fileInput      = document.getElementById("fileInput");
const selectedFileName = document.getElementById("selectedFileName");

// ── Study payload builder ─────────────────────────────────────────────────────
function getStudyPayload(extra = {}) {
  return {
    text:      noteText?.value || "",
    title:     noteTitle?.value?.trim() || "",
    file_name: currentUploadedFileName,
    ...extra,
  };
}

function requireText() {
  if (!noteText || !noteText.value.trim()) throw new Error("Please enter or upload note content first.");
}

// ── File upload ───────────────────────────────────────────────────────────────
// Trigger buttons that may exist on any page
document.getElementById("uploadTriggerBtn")?.addEventListener("click", () => fileInput?.click());
document.getElementById("attachFileBtn")?.addEventListener("click", () => {
  closeAttachMenu();
  fileInput?.click();
});

fileInput?.addEventListener("change", async () => {
  const file = fileInput?.files?.[0];
  currentUploadedFileName = file ? file.name : "";
  if (selectedFileName) {
    selectedFileName.textContent = file ? file.name : "";
    selectedFileName.style.display = file ? "" : "none";
    selectedFileName.hidden = !file;
  }
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);
  try {
    setLoading(true, "Extracting text from file…");
    const response = await fetch("/api/study/upload", { method: "POST", body: formData });
    const raw = await response.text();
    const data = raw ? JSON.parse(raw) : {};
    if (!response.ok) throw new Error(data.detail || "Upload failed.");
    // populate whichever text area is on this page
    const targetTextarea = document.getElementById("noteText") || document.getElementById("audioText");
    if (targetTextarea) { targetTextarea.value = data.extracted_text; autoResize(targetTextarea); }
    currentUploadedFileName = data.filename || "";
    if (selectedFileName) {
      selectedFileName.textContent = `📄 ${data.filename}`;
      selectedFileName.style.display = "";
      selectedFileName.hidden = false;
    }
    updateMetrics();
    showFeedback("File uploaded and text extracted.");
  } catch (err) {
    showFeedback(err.message);
  } finally {
    setLoading(false);
  }
});

// ── Attach menu (dashboard composer + button) ─────────────────────────────────
const attachBtn  = document.getElementById("attachBtn");
const attachMenu = document.getElementById("attachMenu");

function openAttachMenu() {
  if (!attachMenu) return;
  attachMenu.classList.add("open");
  attachMenu.setAttribute("aria-hidden", "false");
  attachBtn?.setAttribute("aria-expanded", "true");
}
function closeAttachMenu() {
  if (!attachMenu) return;
  attachMenu.classList.remove("open");
  attachMenu.setAttribute("aria-hidden", "true");
  attachBtn?.setAttribute("aria-expanded", "false");
}

attachBtn?.addEventListener("click", e => {
  e.stopPropagation();
  attachMenu?.classList.contains("open") ? closeAttachMenu() : openAttachMenu();
});
document.addEventListener("click", e => {
  if (attachMenu && !document.getElementById("attachWrap")?.contains(e.target)) closeAttachMenu();
});
document.addEventListener("keydown", e => { if (e.key === "Escape") closeAttachMenu(); });

document.getElementById("attachAudioBtn")?.addEventListener("click", () => {
  closeAttachMenu();
  const text = noteText?.value.trim();
  if (!text) { showFeedback("Add some text first to listen to it."); return; }
  speakText(text);
});

document.getElementById("attachPasteBtn")?.addEventListener("click", async () => {
  closeAttachMenu();
  try {
    const text = await navigator.clipboard.readText();
    if (!text.trim()) { showFeedback("Clipboard is empty."); return; }
    if (noteText) {
      noteText.value = (noteText.value ? noteText.value + "\n\n" : "") + text;
      autoResize(noteText);
      updateMetrics();
    }
    showFeedback("Pasted from clipboard.");
  } catch {
    showFeedback("Clipboard access denied. Use Ctrl+V to paste.");
  }
});

document.getElementById("attachClearBtn")?.addEventListener("click", () => {
  closeAttachMenu();
  if (noteText) { noteText.value = ""; autoResize(noteText); }
  if (noteTitle) noteTitle.value = "";
  currentUploadedFileName = "";
  if (selectedFileName) { selectedFileName.textContent = ""; selectedFileName.style.display = "none"; }
  if (fileInput) fileInput.value = "";
  updateMetrics();
  showFeedback("Workspace cleared.");
});

// ── Render helpers ────────────────────────────────────────────────────────────
const summaryResults     = document.getElementById("summaryResults");
const explanationResults = document.getElementById("explanationResults");
const keywordResults     = document.getElementById("keywordResults");
const summaryFeedbackPanel     = document.getElementById("summaryFeedbackPanel");
const explanationFeedbackPanel = document.getElementById("explanationFeedbackPanel");
const summaryCorrectionInput   = document.getElementById("summaryCorrectionInput");
const explanationCorrectionInput = document.getElementById("explanationCorrectionInput");

function renderSummary(bullets) {
  if (!summaryResults) return;
  summaryResults.innerHTML = "";
  const summaryEmpty = document.getElementById("summaryEmpty");
  if (summaryEmpty) summaryEmpty.style.display = "none";
  bullets.forEach(bullet => {
    const li = document.createElement("li");
    li.textContent = bullet;
    summaryResults.appendChild(li);
  });
  if (summaryFeedbackPanel) {
    summaryFeedbackPanel.style.display = "";
    summaryFeedbackPanel.classList.remove("d-none");
  }
  if (summaryCorrectionInput) summaryCorrectionInput.value = bullets.join("\n");
  animateBlock(summaryResults);
}

function renderExplanation(lines) {
  if (!explanationResults) return;
  explanationResults.innerHTML = "";
  const explanationEmpty = document.getElementById("explanationEmpty");
  if (explanationEmpty) explanationEmpty.style.display = "none";
  lines.forEach(line => {
    const div = document.createElement("div");
    div.textContent = line;
    explanationResults.appendChild(div);
  });
  if (explanationFeedbackPanel) {
    explanationFeedbackPanel.style.display = "";
    explanationFeedbackPanel.classList.remove("d-none");
  }
  if (explanationCorrectionInput) explanationCorrectionInput.value = lines.join("\n");
  animateBlock(explanationResults);
}

function renderKeywords(keywords) {
  if (!keywordResults) return;
  keywordResults.innerHTML = "";
  if (!keywords || !keywords.length) {
    keywordResults.innerHTML = "<span class='meta-pill'>No keywords</span>";
    return;
  }
  keywords.forEach(kw => {
    const chip = document.createElement("span");
    chip.className = "meta-pill";
    chip.textContent = kw;
    keywordResults.appendChild(chip);
  });
  animateBlock(keywordResults);
}

// ── Feedback rating helpers ───────────────────────────────────────────────────
const summaryLikeBtn    = document.getElementById("summaryLikeBtn");
const summaryDislikeBtn = document.getElementById("summaryDislikeBtn");
const explanationLikeBtn    = document.getElementById("explanationLikeBtn");
const explanationDislikeBtn = document.getElementById("explanationDislikeBtn");

function setFeedbackRating(type, rating) {
  if (type === "summary") {
    summaryRating = rating;
    summaryLikeBtn?.classList.toggle("active", rating === 1);
    summaryDislikeBtn?.classList.toggle("active", rating === -1);
  } else {
    explanationRating = rating;
    explanationLikeBtn?.classList.toggle("active", rating === 1);
    explanationDislikeBtn?.classList.toggle("active", rating === -1);
  }
}

async function submitOutputFeedback(featureType, aiOutput, correctedOutput, rating) {
  const originalText = noteText?.value.trim() || "";
  if (!originalText || !aiOutput.trim()) { showFeedback("Generate an output before sending feedback."); return; }
  await requestJson("/api/study/feedback", {
    method: "POST",
    body: JSON.stringify({
      feature_type: featureType,
      original_text: originalText,
      ai_output: aiOutput,
      user_corrected_output: correctedOutput.trim(),
      rating,
    }),
  });
}

// ── Summarizer ────────────────────────────────────────────────────────────────
const summarizeBtn = document.getElementById("summarizeBtn");

summarizeBtn?.addEventListener("click", async () => {
  try {
    requireText();
    setLoading(true, "Summarizing your notes… this takes ~10 seconds");
    const data = await requestJson("/api/study/summarize", {
      method: "POST",
      body: JSON.stringify(getStudyPayload()),
    });
    currentSummary = data.bullets;
    summaryRating  = null;
    setFeedbackRating("summary", null);
    renderSummary(data.bullets);
    renderKeywords(data.keywords || []);
    showFeedback("Summary ready.");
  } catch (err) {
    showFeedback(err.message);
  } finally {
    setLoading(false);
  }
});

// Feedback panel wiring (summarizer)
summaryLikeBtn?.addEventListener("click",    () => setFeedbackRating("summary",  1));
summaryDislikeBtn?.addEventListener("click", () => setFeedbackRating("summary", -1));

document.getElementById("copySummaryBtn")?.addEventListener("click", () => {
  copyText(summaryResults?.innerText || "", "Summary copied!");
});

document.getElementById("regenerateSummaryBtn")?.addEventListener("click", () => {
  summarizeBtn?.click();
});

document.getElementById("toggleSummaryEditorBtn")?.addEventListener("click", () => {
  const wrap = document.getElementById("summaryEditorWrap");
  if (!wrap) return;
  const visible = wrap.style.display !== "none";
  wrap.style.display = visible ? "none" : "";
});

document.getElementById("submitSummaryFeedbackBtn")?.addEventListener("click", async () => {
  try {
    const corrected = document.getElementById("summaryCorrectionInput")?.value || "";
    await submitOutputFeedback("summary", currentSummary.join("\n"), corrected, summaryRating);
    showFeedback("Feedback saved — thank you!");
  } catch (err) {
    showFeedback(err.message);
  }
});

// ── Explainer ─────────────────────────────────────────────────────────────────
const explainBtn = document.getElementById("explainBtn");

explainBtn?.addEventListener("click", async () => {
  try {
    requireText();
    setLoading(true, "Generating explanation… this takes ~10 seconds");
    const data = await requestJson("/api/study/explain", {
      method: "POST",
      body: JSON.stringify(getStudyPayload({ level: currentLevel })),
    });
    currentExplanation = data.explanation;
    explanationRating  = null;
    setFeedbackRating("explanation", null);
    renderExplanation(data.explanation);
    renderKeywords(data.keywords || []);
    showFeedback(`Explanation ready (${currentLevel} level).`);
  } catch (err) {
    showFeedback(err.message);
  } finally {
    setLoading(false);
  }
});

// Feedback panel wiring (explainer)
explanationLikeBtn?.addEventListener("click",    () => setFeedbackRating("explanation",  1));
explanationDislikeBtn?.addEventListener("click", () => setFeedbackRating("explanation", -1));

document.getElementById("toggleExplanationEditorBtn")?.addEventListener("click", () => {
  const wrap = document.getElementById("explanationEditorWrap");
  if (!wrap) return;
  wrap.style.display = wrap.style.display !== "none" ? "none" : "";
});

document.getElementById("submitExplanationFeedbackBtn")?.addEventListener("click", async () => {
  try {
    const corrected = document.getElementById("explanationCorrectionInput")?.value || "";
    await submitOutputFeedback("explanation", currentExplanation.join("\n"), corrected, explanationRating);
    showFeedback("Feedback saved — thank you!");
  } catch (err) {
    showFeedback(err.message);
  }
});

// ── Level buttons (.level-btn) — wired on Explainer & Dashboard ───────────────
document.querySelectorAll(".level-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    currentLevel = btn.dataset.level || "basic";
    document.querySelectorAll(".level-btn").forEach(b => {
      b.classList.toggle("active", b === btn);
      b.setAttribute("aria-pressed", String(b === btn));
    });
    // Show/hide the level switcher in the dashboard tool bar when "explain" is active
    const levelSwitcher = document.getElementById("levelSwitcher");
    if (levelSwitcher) levelSwitcher.style.display = "";
  });
});

// ── Study Toolbox (Explainer page sidebar) ────────────────────────────────────
const saveBtn = document.getElementById("saveBtn");

async function doSaveSession() {
  if (!getToken()) { showFeedback("Please log in to save sessions."); return; }
  const text = noteText?.value?.trim() || "";
  if (!text) { showFeedback("There is nothing to save yet."); return; }
  try {
    setLoading(true, "Saving session…");
    const summaryForSave = currentSummary.length ? currentSummary.join("\n") : undefined;
    const explanationForSave = currentExplanation.length ? currentExplanation.join("\n") : undefined;
    const noteTypeVal = currentExplanation.length ? "explanation"
      : currentSummary.length ? "summary" : undefined;
    await requestJson("/api/study/save", {
      method: "POST",
      body: JSON.stringify({
        title:         noteTitle?.value?.trim() || text.slice(0, 60),
        original_text: text,
        summary:       summaryForSave,
        explanation:   explanationForSave,
        note_type:     noteTypeVal,
      }),
    }, true);
    showFeedback("Session saved!");
  } catch (err) {
    showFeedback(err.message);
  } finally {
    setLoading(false);
  }
}

saveBtn?.addEventListener("click", doSaveSession);
document.getElementById("saveSessionToolboxBtn")?.addEventListener("click", doSaveSession);

// Copy explanation toolbox button
document.getElementById("copyExplanationBtn")?.addEventListener("click", () => {
  copyText(explanationResults?.innerText || "", "Explanation copied!");
});
document.getElementById("copyExplanationBtnToolbox")?.addEventListener("click", () => {
  copyText(explanationResults?.innerText || "", "Explanation copied!");
});

// ── Listen button (TTS for explanation) ───────────────────────────────────────
document.getElementById("listenBtn")?.addEventListener("click", () => {
  const text = explanationResults?.innerText?.trim() || noteText?.value?.trim() || "";
  if (!text) { showFeedback("Generate an explanation first."); return; }
  speakText(text);
});

// ═══════════════════════════════════════════════════════════════════════════════
// QUIZ ENGINE
// ═══════════════════════════════════════════════════════════════════════════════
const generateQuizBtn = document.getElementById("generateQuizBtn");
const inputCard       = document.getElementById("inputCard");
const questionCard    = document.getElementById("questionCard");
const completionCard  = document.getElementById("completionCard");
const questionNumber  = document.getElementById("questionNumber");
const questionText    = document.getElementById("questionText");
const optionsList     = document.getElementById("optionsList");
const feedbackMsg     = document.getElementById("feedbackMsg");
const nextBtn         = document.getElementById("nextBtn");
const finishBtn       = document.getElementById("finishBtn");
const finalScore      = document.getElementById("finalScore");
const restartBtn      = document.getElementById("restartBtn");
const correctCount    = document.getElementById("correctCount");
const incorrectCount  = document.getElementById("incorrectCount");
const streakCount     = document.getElementById("streakCount");

let quizQuestions    = [];
let quizIndex        = 0;
let quizCorrect      = 0;
let quizIncorrect    = 0;
let quizStreak       = 0;
let quizAnswered     = false;

function updateQuizStats() {
  if (correctCount)   correctCount.textContent   = String(quizCorrect);
  if (incorrectCount) incorrectCount.textContent = String(quizIncorrect);
  if (streakCount)    streakCount.textContent    = String(quizStreak);
}

function showQuizQuestion(index) {
  const q = quizQuestions[index];
  if (!q) return;
  quizAnswered = false;
  if (questionNumber) questionNumber.textContent = `Question ${index + 1} of ${quizQuestions.length}`;
  if (questionText)   questionText.textContent   = q.question;
  if (feedbackMsg)    feedbackMsg.textContent    = "";
  if (nextBtn)        nextBtn.style.display      = "none";
  if (finishBtn)      finishBtn.style.display    = "none";

  if (optionsList) {
    optionsList.innerHTML = "";
    q.options.forEach((option, i) => {
      const btn = document.createElement("button");
      btn.type      = "button";
      btn.className = "btn btn-ghost quiz-option";
      const labels  = ["A", "B", "C", "D"];
      btn.dataset.option  = labels[i] || String(i + 1);
      const isCorrect     = option === q.answer;
      btn.dataset.correct = String(isCorrect);
      btn.setAttribute("role", "listitem");
      btn.setAttribute("aria-label", `Option ${labels[i] || i + 1}: ${option}`);
      btn.textContent = option;
      btn.addEventListener("click", () => handleQuizAnswer(btn, isCorrect));
      optionsList.appendChild(btn);
    });
  }
}

function handleQuizAnswer(selectedBtn, isCorrect) {
  if (quizAnswered) return;
  quizAnswered = true;

  // Highlight all options — green for correct, red for wrong selected
  optionsList?.querySelectorAll(".quiz-option").forEach(btn => {
    btn.disabled = true;
    if (btn.dataset.correct === "true") {
      btn.classList.add("correct");
      btn.style.borderColor  = "var(--color-success, #22c55e)";
      btn.style.background   = "rgba(34,197,94,0.12)";
    } else if (btn === selectedBtn) {
      btn.classList.add("incorrect");
      btn.style.borderColor = "var(--color-error, #ef4444)";
      btn.style.background  = "rgba(239,68,68,0.12)";
    }
  });

  if (isCorrect) {
    quizCorrect++;
    quizStreak++;
    if (feedbackMsg) { feedbackMsg.textContent = "✓ Correct!"; feedbackMsg.style.color = "#22c55e"; }
  } else {
    quizIncorrect++;
    quizStreak = 0;
    if (feedbackMsg) { feedbackMsg.textContent = "✗ Incorrect — see the correct answer highlighted."; feedbackMsg.style.color = "#ef4444"; }
  }
  updateQuizStats();

  // Show next / finish
  const isLast = quizIndex >= quizQuestions.length - 1;
  if (nextBtn)   nextBtn.style.display   = isLast ? "none"   : "";
  if (finishBtn) finishBtn.style.display = isLast ? "" : "none";
}

nextBtn?.addEventListener("click", () => {
  quizIndex++;
  if (quizIndex < quizQuestions.length) {
    showQuizQuestion(quizIndex);
  } else {
    showCompletionCard();
  }
});

finishBtn?.addEventListener("click", () => showCompletionCard());

function showCompletionCard() {
  if (questionCard)  questionCard.style.display  = "none";
  if (completionCard) {
    completionCard.style.display = "";
    completionCard.hidden = false;
  }
  const total = quizQuestions.length;
  if (finalScore) {
    finalScore.innerHTML = `
      <strong>${quizCorrect} / ${total}</strong> correct
      <br><span style="color:var(--on-surface-muted);font-size:0.9rem;">
        ${quizIncorrect} incorrect &nbsp;·&nbsp; best streak tracked in stats
      </span>`;
  }
}

restartBtn?.addEventListener("click", () => {
  quizQuestions = [];
  quizIndex = quizCorrect = quizIncorrect = quizStreak = 0;
  updateQuizStats();
  if (completionCard) completionCard.style.display = "none";
  if (questionCard)   questionCard.style.display   = "none";
  if (inputCard) { inputCard.style.display = ""; inputCard.hidden = false; }
});

document.getElementById("saveQuizBtn")?.addEventListener("click", async () => {
  if (!getToken()) { showFeedback("Please log in to save sessions."); return; }
  if (!quizQuestions.length) { showFeedback("There is no quiz to save yet."); return; }
  const text = noteText?.value?.trim() || "";
  try {
    setLoading(true, "Saving quiz…");
    await requestJson("/api/study/save", {
      method: "POST",
      body: JSON.stringify({
        title:         noteTitle?.value?.trim() || text.slice(0, 60) || "Quiz session",
        original_text: text || "Quiz generated from uploaded material.",
        quiz:          JSON.stringify(quizQuestions),
        note_type:     "quiz",
      }),
    }, true);
    showFeedback("Quiz saved!");
  } catch (err) {
    showFeedback(err.message);
  } finally {
    setLoading(false);
  }
});

generateQuizBtn?.addEventListener("click", async () => {
  try {
    requireText();
    setLoading(true, "Building quiz questions…");
    const data = await requestJson("/api/study/quiz", {
      method: "POST",
      body: JSON.stringify(getStudyPayload()),
    });
    quizQuestions = data.questions || [];
    if (!quizQuestions.length) { showFeedback("No questions returned. Try more detailed notes."); return; }
    quizIndex = quizCorrect = quizIncorrect = quizStreak = 0;
    updateQuizStats();
    if (inputCard)      { inputCard.style.display = "none"; inputCard.hidden = true; }
    if (completionCard) { completionCard.style.display = "none"; }
    if (questionCard)   { questionCard.style.display = ""; questionCard.hidden = false; }
    showQuizQuestion(0);
    showFeedback("Quiz ready!");
  } catch (err) {
    showFeedback(err.message);
  } finally {
    setLoading(false);
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDES PRESENTER
// ═══════════════════════════════════════════════════════════════════════════════
const generateSlidesBtn = document.getElementById("generateSlidesBtn");
const inputState        = document.getElementById("inputState");
const presenterState    = document.getElementById("presenterState");
const slidesList        = document.getElementById("slidesList");
const slideTitle        = document.getElementById("slideTitle");
const slidePoints       = document.getElementById("slidePoints");
const toggleSettingsBtn = document.getElementById("toggleSettingsBtn");

let slidesData = [];

function renderSlidesList(slides) {
  if (!slidesList) return;
  slidesList.innerHTML = "";
  slides.forEach((slide, index) => {
    const card = document.createElement("div");
    card.className = "slides-thumb-card" + (index === 0 ? " active" : "");
    card.setAttribute("role", "button");
    card.setAttribute("tabindex", "0");
    card.setAttribute("aria-label", `Slide ${index + 1}: ${slide.title}`);
    card.innerHTML = `<span class="slide-number">${index + 1}</span><span class="slide-thumb-title">${slide.title}</span>`;
    card.addEventListener("click", () => activateSlide(index));
    card.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); activateSlide(index); } });
    slidesList.appendChild(card);
  });
}

function activateSlide(index) {
  const slide = slidesData[index];
  if (!slide) return;
  // Update active thumbnail
  slidesList?.querySelectorAll(".slides-thumb-card").forEach((card, i) => {
    card.classList.toggle("active", i === index);
  });
  // Update canvas
  if (slideTitle) slideTitle.textContent = slide.title;
  if (slidePoints) {
    slidePoints.innerHTML = "";
    (slide.points || []).forEach(point => {
      const li = document.createElement("li");
      li.textContent = point;
      slidePoints.appendChild(li);
    });
  }
}

document.getElementById("saveSlidesBtn")?.addEventListener("click", async () => {
  if (!getToken()) { showFeedback("Please log in to save sessions."); return; }
  if (!slidesData.length) { showFeedback("There is no slide deck to save yet."); return; }
  const text = noteText?.value?.trim() || "";
  try {
    setLoading(true, "Saving slides…");
    await requestJson("/api/study/save", {
      method: "POST",
      body: JSON.stringify({
        title:         noteTitle?.value?.trim() || text.slice(0, 60) || "Slide deck",
        original_text: text || "Slides generated from uploaded material.",
        slides:        JSON.stringify(slidesData),
        note_type:     "slides",
      }),
    }, true);
    showFeedback("Slides saved!");
  } catch (err) {
    showFeedback(err.message);
  } finally {
    setLoading(false);
  }
});

generateSlidesBtn?.addEventListener("click", async () => {
  try {
    requireText();
    setLoading(true, "Building slide outline…");
    const data = await requestJson("/api/study/slides", {
      method: "POST",
      body: JSON.stringify(getStudyPayload()),
    });
    slidesData = data.slides || [];
    if (!slidesData.length) { showFeedback("No slides returned. Try more detailed notes."); return; }
    currentSlides = slidesData;
    // Switch views
    if (inputState) { inputState.style.display = "none"; inputState.hidden = true; }
    if (presenterState) { presenterState.style.display = ""; presenterState.hidden = false; }
    renderSlidesList(slidesData);
    activateSlide(0);
    showFeedback("Slides ready!");
  } catch (err) {
    showFeedback(err.message);
  } finally {
    setLoading(false);
  }
});

// Toggle settings panel at < 1024px
toggleSettingsBtn?.addEventListener("click", () => {
  const settings = document.querySelector(".slides-settings");
  if (!settings) return;
  if (window.innerWidth < 1024) {
    const visible = settings.style.display !== "none" && !settings.hidden;
    settings.style.display = visible ? "none" : "";
    settings.hidden = visible;
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
// AUDIO PAGE
// ═══════════════════════════════════════════════════════════════════════════════
const playAudioBtn      = document.getElementById("playAudioBtn");
const pauseAudioBtn     = document.getElementById("pauseAudioBtn");
const stopAudioBtn      = document.getElementById("stopAudioBtn");
const audioStatus       = document.getElementById("audioStatus");
const speedSlider       = document.getElementById("speedSlider");
const speedReadout      = document.getElementById("speedReadout");
const voiceSelect       = document.getElementById("voiceSelect");
const stabilitySlider   = document.getElementById("stabilitySlider");
const stabilityReadout  = document.getElementById("stabilityReadout");
const similaritySlider  = document.getElementById("similaritySlider");
const similarityReadout = document.getElementById("similarityReadout");
const ttsModeNote       = document.getElementById("ttsModeNote");
const elevenAudioPlayer = document.getElementById("elevenAudioPlayer");

let speechUtterance = null;
let ttsConfigured = false;   // true once we confirm an ElevenLabs key is set server-side
let elevenVoices = [];

// Ask the backend whether ElevenLabs is configured and which voices exist.
async function loadTtsVoices() {
  try {
    const res = await fetch("/api/study/tts/voices");
    if (!res.ok) throw new Error("voices request failed");
    const data = await res.json();
    ttsConfigured = Boolean(data.configured);
    elevenVoices = Array.isArray(data.voices) ? data.voices : [];
  } catch {
    ttsConfigured = false;
    elevenVoices = [];
  }
  populateVoiceList();
  updateTtsModeNote();
}

// Populate voice dropdown — ElevenLabs voices when configured, browser voices otherwise.
function populateVoiceList() {
  if (!voiceSelect) return;

  if (ttsConfigured && elevenVoices.length) {
    voiceSelect.innerHTML = "";
    elevenVoices.forEach(voice => {
      const opt = document.createElement("option");
      opt.value = voice.voice_id;
      opt.dataset.eleven = "true";
      opt.textContent = voice.description ? `${voice.name} — ${voice.description}` : voice.name;
      voiceSelect.appendChild(opt);
    });
    if (stabilityField) stabilityField.hidden = false;
    if (similarityField) similarityField.hidden = false;
    return;
  }

  // Fallback: browser SpeechSynthesis voices
  if (stabilityField) stabilityField.hidden = true;
  if (similarityField) similarityField.hidden = true;
  if (typeof speechSynthesis === "undefined") return;
  const voices = speechSynthesis.getVoices();
  if (!voices.length) return;
  voiceSelect.innerHTML = "";
  voices.forEach((voice, i) => {
    const opt = document.createElement("option");
    opt.value = i;
    opt.textContent = `${voice.name} (${voice.lang})`;
    voiceSelect.appendChild(opt);
  });
}

const stabilityField  = document.getElementById("stabilityField");
const similarityField = document.getElementById("similarityField");

function updateTtsModeNote() {
  if (!ttsModeNote) return;
  ttsModeNote.textContent = ttsConfigured
    ? "Using ElevenLabs AI voices."
    : "ElevenLabs isn't configured — using your browser's built-in voice instead.";
}

if (typeof speechSynthesis !== "undefined") {
  speechSynthesis.onvoiceschanged = () => { if (!ttsConfigured) populateVoiceList(); };
}
loadTtsVoices();

function showAudioStatus(show) {
  if (!audioStatus) return;
  audioStatus.style.display = show ? "" : "none";
  audioStatus.hidden = !show;
}

function speakWithBrowser(text) {
  if (typeof speechSynthesis === "undefined") return;
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = speedSlider ? (parseFloat(speedSlider.value) || 1.0) : 0.95;
  if (voiceSelect && voiceSelect.value !== "" && voiceSelect.selectedOptions[0]?.dataset.eleven !== "true") {
    const voices = speechSynthesis.getVoices();
    const idx = parseInt(voiceSelect.value, 10);
    if (voices[idx]) utterance.voice = voices[idx];
  }
  utterance.onstart = () => showAudioStatus(true);
  utterance.onend   = () => showAudioStatus(false);
  utterance.onerror = () => showAudioStatus(false);
  speechSynthesis.speak(utterance);
  speechUtterance = utterance;
}

async function speakWithElevenLabs(text) {
  const voiceId = (voiceSelect && voiceSelect.selectedOptions[0]?.dataset.eleven === "true")
    ? voiceSelect.value
    : "EXAVITQu4vr4xnSDxMaL";
  const body = {
    text,
    voice_id: voiceId,
    stability: stabilitySlider ? parseFloat(stabilitySlider.value) : 0.5,
    similarity: similaritySlider ? parseFloat(similaritySlider.value) : 0.75,
    speed: speedSlider ? parseFloat(speedSlider.value) : 1.0,
  };
  const res = await fetch("/api/study/tts/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("ElevenLabs request failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  if (!elevenAudioPlayer) throw new Error("No audio element available");
  elevenAudioPlayer.src = url;
  elevenAudioPlayer.onplay  = () => showAudioStatus(true);
  elevenAudioPlayer.onended = () => showAudioStatus(false);
  elevenAudioPlayer.onpause = () => showAudioStatus(false);
  await elevenAudioPlayer.play();
}

// Core TTS function used across pages (dashboard "Listen", summarizer/explainer toolbox, audio page)
function speakText(text) {
  if (!text || !text.trim()) return;
  if (typeof speechSynthesis !== "undefined") speechSynthesis.cancel();
  if (elevenAudioPlayer) elevenAudioPlayer.pause();

  if (ttsConfigured) {
    speakWithElevenLabs(text).catch(() => speakWithBrowser(text));
  } else {
    speakWithBrowser(text);
  }
}

playAudioBtn?.addEventListener("click", () => {
  const audioText = document.getElementById("audioText");
  const text = audioText?.value?.trim() || noteText?.value?.trim() || "";
  if (!text) { showFeedback("Paste some text to listen to first."); return; }
  speakText(text);
});

pauseAudioBtn?.addEventListener("click", () => {
  if (elevenAudioPlayer && !elevenAudioPlayer.paused && elevenAudioPlayer.src) {
    elevenAudioPlayer.pause();
    return;
  }
  if (elevenAudioPlayer && elevenAudioPlayer.paused && elevenAudioPlayer.src && elevenAudioPlayer.currentTime > 0) {
    elevenAudioPlayer.play();
    return;
  }
  if (typeof speechSynthesis === "undefined") return;
  if (speechSynthesis.speaking && !speechSynthesis.paused) {
    speechSynthesis.pause();
  } else if (speechSynthesis.paused) {
    speechSynthesis.resume();
  }
});

stopAudioBtn?.addEventListener("click", () => {
  if (elevenAudioPlayer) {
    elevenAudioPlayer.pause();
    elevenAudioPlayer.currentTime = 0;
  }
  if (typeof speechSynthesis !== "undefined") speechSynthesis.cancel();
  showAudioStatus(false);
});

// Monitor speaking state to keep status indicator in sync (browser-voice path only)
function pollAudioStatus() {
  if (ttsConfigured) return; // ElevenLabs path drives status via audio element events
  if (typeof speechSynthesis !== "undefined" && audioStatus) {
    showAudioStatus(speechSynthesis.speaking);
  }
}
setInterval(pollAudioStatus, 500);

// Speed slider readout
speedSlider?.addEventListener("input", () => {
  const val = parseFloat(speedSlider.value).toFixed(1);
  if (speedReadout) speedReadout.textContent = `${val}x`;
  speedSlider.setAttribute("aria-valuenow", val);
});

stabilitySlider?.addEventListener("input", () => {
  const val = parseFloat(stabilitySlider.value).toFixed(2);
  if (stabilityReadout) stabilityReadout.textContent = val;
  stabilitySlider.setAttribute("aria-valuenow", val);
});

similaritySlider?.addEventListener("input", () => {
  const val = parseFloat(similaritySlider.value).toFixed(2);
  if (similarityReadout) similarityReadout.textContent = val;
  similaritySlider.setAttribute("aria-valuenow", val);
});

// ═══════════════════════════════════════════════════════════════════════════════
// DASHBOARD — recent sessions + sendBtn tool dispatch
// ═══════════════════════════════════════════════════════════════════════════════

// Tool pill state — shared between welcome pills and toolbar pills
let activeTool = "summarize";

function setActiveTool(tool) {
  activeTool = tool;
  document.querySelectorAll(".tool-pill").forEach(pill => {
    const isActive = pill.dataset.tool === tool;
    pill.classList.toggle("active", isActive);
    pill.setAttribute("aria-pressed", String(isActive));
  });
  // Show level switcher only for explain
  const levelSwitcher = document.getElementById("levelSwitcher");
  if (levelSwitcher) levelSwitcher.style.display = tool === "explain" ? "" : "none";
}

document.querySelectorAll(".tool-pill").forEach(pill => {
  pill.addEventListener("click", () => setActiveTool(pill.dataset.tool));
});

// ── Inline Q&A chat ("Ask a Question" tool) ───────────────────────────────────
const chatMessages = document.getElementById("chatMessages");

function appendChatBubble(role, text) {
  if (!chatMessages) return null;
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble chat-bubble-${role === "user" ? "user" : "ai"}`;
  const label = document.createElement("div");
  label.className = "chat-bubble-label";
  label.textContent = role === "user" ? "You" : "StudyMate AI";
  const body = document.createElement("div");
  body.className = "chat-bubble-body";
  body.textContent = text;
  bubble.appendChild(label);
  bubble.appendChild(body);
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return bubble;
}

function appendTypingIndicator() {
  if (!chatMessages) return null;
  const typing = document.createElement("div");
  typing.className = "chat-typing";
  typing.innerHTML = "<span></span><span></span><span></span>";
  chatMessages.appendChild(typing);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return typing;
}

async function askQuestion(question, context = "") {
  appendChatBubble("user", question);
  const typing = appendTypingIndicator();
  try {
    const data = await requestJson("/api/study/ask", {
      method: "POST",
      body: JSON.stringify({ question, context }),
    });
    typing?.remove();
    appendChatBubble("ai", data.answer || "I couldn't find an answer for that.");
  } catch (err) {
    typing?.remove();
    appendChatBubble("ai", `Something went wrong: ${err.message}`);
  }
}

// sendBtn — answers directly for "Ask", otherwise stashes text and routes to the right tool page
const sendBtn = document.getElementById("sendBtn");
sendBtn?.addEventListener("click", async () => {
  const text = noteText?.value?.trim() || "";
  if (!text) { showFeedback("Please paste or type your notes first."); return; }

  // Hide welcome banner after first submit
  const chatWelcome = document.querySelector(".chat-welcome");
  if (chatWelcome) chatWelcome.style.display = "none";

  if (activeTool === "ask") {
    noteText.value = "";
    autoResize(noteText);
    updateMetrics();
    await askQuestion(text);
    return;
  }

  const toolRoutes = { summarize: "/app/summarizer", explain: "/app/explainer", quiz: "/app/quiz", slides: "/app/slides" };
  // For dashboard, stash the text and redirect to the relevant tool page
  if (toolRoutes[activeTool]) {
    try {
      sessionStorage.setItem("studymate-pending-text", text);
      sessionStorage.setItem("studymate-pending-tool", activeTool);
    } catch { /* storage unavailable */ }
    window.location.href = toolRoutes[activeTool];
  }
});

// Restore pending text on tool pages (set by sendBtn redirect above)
(function restorePendingText() {
  const pendingText = sessionStorage.getItem("studymate-pending-text");
  const pendingTool = sessionStorage.getItem("studymate-pending-tool");
  if (!pendingText) return;
  sessionStorage.removeItem("studymate-pending-text");
  sessionStorage.removeItem("studymate-pending-tool");
  if (noteText) {
    noteText.value = pendingText;
    autoResize(noteText);
    updateMetrics();
  }
  // Auto-trigger if on the right page
  const path = window.location.pathname;
  if (pendingTool === "summarize" && path.includes("summarizer")) {
    setTimeout(() => summarizeBtn?.click(), 200);
  } else if (pendingTool === "explain" && path.includes("explainer")) {
    setTimeout(() => explainBtn?.click(), 200);
  } else if (pendingTool === "quiz" && path.includes("quiz")) {
    setTimeout(() => generateQuizBtn?.click(), 200);
  } else if (pendingTool === "slides" && path.includes("slides")) {
    setTimeout(() => generateSlidesBtn?.click(), 200);
  }
})();

// ── Dashboard: recent sessions grid ──────────────────────────────────────────
const sessionsGrid = document.getElementById("sessionsGrid");

function buildSessionCard(note) {
  const article = document.createElement("article");
  article.className = "saved-note-card";
  article.dataset.type = note.note_type || "summary";
  const typeLabel = note.note_type
    ? note.note_type.charAt(0).toUpperCase() + note.note_type.slice(1)
    : "Summary";
  const preview = (note.summary || note.explanation || note.original_text || "").slice(0, 140);
  const dateStr = note.created_at ? new Date(note.created_at).toLocaleDateString() : "";
  const toolHref = {
    summary:     "/app/summarizer",
    explanation: "/app/explainer",
    quiz:        "/app/quiz",
    slides:      "/app/slides",
  }[note.note_type] || "/app/summarizer";
  article.innerHTML = `
    <span class="status-badge">${typeLabel}</span>
    <h4>${note.title || "Untitled Session"}</h4>
    <p class="small-feedback">${dateStr}</p>
    <p class="panel-copy">${preview}${preview.length >= 140 ? "…" : ""}</p>
    <div class="card-hover-action">
      <a class="btn btn-primary" href="${toolHref}" aria-label="View session: ${note.title || 'Untitled'}">View Session</a>
    </div>`;
  return article;
}

async function loadRecentSessions() {
  if (!sessionsGrid) return;
  if (!getToken()) {
    sessionsGrid.innerHTML = "<p class='empty-copy'>Log in to see your recent sessions.</p>";
    return;
  }
  try {
    const notes = await requestJson("/api/study/history", { method: "GET" }, true);
    sessionsGrid.innerHTML = "";
    const emptyEl = document.getElementById("sessionsEmpty");
    if (!notes || !notes.length) {
      if (emptyEl) { emptyEl.style.display = ""; emptyEl.hidden = false; }
      else sessionsGrid.innerHTML = "<p class='empty-copy'>No saved sessions yet.</p>";
      return;
    }
    if (emptyEl) emptyEl.style.display = "none";
    const recent = notes.slice(0, 3);
    recent.forEach(note => sessionsGrid.appendChild(buildSessionCard(note)));
    animateBlock(sessionsGrid);
  } catch {
    sessionsGrid.innerHTML = "<p class='empty-copy'>Could not load sessions.</p>";
  }
}

if (sessionsGrid) loadRecentSessions();

// ═══════════════════════════════════════════════════════════════════════════════
// SAVED NOTES PAGE — tabbed filtering
// ═══════════════════════════════════════════════════════════════════════════════
const savedGrid  = document.getElementById("savedGrid");
const emptyState = document.getElementById("emptyState");

let allSavedNotes = [];

function filterSavedGrid(filterVal) {
  if (!savedGrid) return;
  const cards = savedGrid.querySelectorAll(".saved-note-card");
  let visibleCount = 0;
  cards.forEach(card => {
    const type    = card.dataset.type || "summary";
    const matches = filterVal === "all" || type === filterVal;
    card.style.display = matches ? "" : "none";
    if (matches) visibleCount++;
  });
  if (emptyState) emptyState.style.display = visibleCount === 0 ? "" : "none";
}

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => {
      b.classList.remove("active");
      b.setAttribute("aria-selected", "false");
    });
    btn.classList.add("active");
    btn.setAttribute("aria-selected", "true");
    filterSavedGrid(btn.dataset.filter || "all");
  });
});

async function loadSavedGrid() {
  if (!savedGrid) return;
  if (!getToken()) {
    savedGrid.innerHTML = "<p class='empty-copy'>Log in to view your saved sessions.</p>";
    return;
  }
  try {
    setLoading(true, "Loading sessions…");
    const notes = await requestJson("/api/study/history", { method: "GET" }, true);
    allSavedNotes = notes || [];
    savedGrid.innerHTML = "";
    if (!allSavedNotes.length) {
      if (emptyState) { emptyState.style.display = ""; emptyState.hidden = false; }
      return;
    }
    if (emptyState) emptyState.style.display = "none";
    allSavedNotes.forEach(note => savedGrid.appendChild(buildSessionCard(note)));
    animateBlock(savedGrid);
    // Apply active filter
    const activeTab = document.querySelector(".tab-btn.active");
    if (activeTab) filterSavedGrid(activeTab.dataset.filter || "all");
  } catch (err) {
    savedGrid.innerHTML = `<p class='empty-copy'>${err.message}</p>`;
  } finally {
    setLoading(false);
  }
}

if (savedGrid) loadSavedGrid();

// ═══════════════════════════════════════════════════════════════════════════════
// PROFILE PAGE — preferences
// ═══════════════════════════════════════════════════════════════════════════════
const savePrefsBtn  = document.getElementById("savePrefsBtn");
const resetPrefsBtn = document.getElementById("resetPrefsBtn");
const prefsFeedback = document.getElementById("prefsFeedback");

const DEFAULT_PREFS = {
  persona:           "student",
  summary_length:    "balanced",
  explanation_style: "standard",
  theme:             "dark",
  accent:            "amber",
  card_style:        "soft",
};

function showPrefsFeedback(msg) {
  if (!prefsFeedback) return;
  prefsFeedback.textContent = msg || "Preferences saved!";
  prefsFeedback.style.display = "";
  prefsFeedback.hidden = false;
  clearTimeout(showPrefsFeedback._timer);
  showPrefsFeedback._timer = setTimeout(() => {
    prefsFeedback.style.display = "none";
    prefsFeedback.hidden = true;
  }, 3000);
}

function applyPrefsToForm(prefs) {
  const personaSel   = document.getElementById("personaSelect");
  const summaryLen   = document.getElementById("summaryLengthSelect");
  const explainStyle = document.getElementById("explanationStyleSelect");
  if (personaSel   && prefs.persona)           personaSel.value   = prefs.persona;
  if (summaryLen   && prefs.summary_length)     summaryLen.value   = prefs.summary_length;
  if (explainStyle && prefs.explanation_style)  explainStyle.value = prefs.explanation_style;
}

let resetPending = false;
let savePending  = false;

resetPrefsBtn?.addEventListener("click", () => {
  resetPending = true;
  // Simultaneous save+reset: reset wins (handled in savePrefsBtn click via flag)
  applyPrefsToForm(DEFAULT_PREFS);
  showPrefsFeedback("Preferences reset to defaults.");
  setTimeout(() => { resetPending = false; }, 50);
});

savePrefsBtn?.addEventListener("click", async () => {
  savePending = true;
  // If reset was also clicked in the same tick, reset wins
  await new Promise(r => setTimeout(r, 0));
  if (resetPending) { savePending = false; return; }
  savePending = false;

  if (!getToken()) { showFeedback("Please log in to save preferences."); return; }
  const persona   = document.getElementById("personaSelect")?.value          || DEFAULT_PREFS.persona;
  const sumLen    = document.getElementById("summaryLengthSelect")?.value     || DEFAULT_PREFS.summary_length;
  const expStyle  = document.getElementById("explanationStyleSelect")?.value  || DEFAULT_PREFS.explanation_style;
  try {
    setLoading(true, "Saving preferences…");
    await requestJson("/api/study/preferences", {
      method: "POST",
      body: JSON.stringify({
        persona,
        summary_length:    sumLen,
        explanation_style: expStyle,
        theme:             DEFAULT_PREFS.theme,
        accent:            DEFAULT_PREFS.accent,
        card_style:        DEFAULT_PREFS.card_style,
      }),
    }, true);
    showPrefsFeedback("Preferences saved!");
  } catch (err) {
    showFeedback(err.message);
  } finally {
    setLoading(false);
  }
});

async function loadPreferences() {
  if (!getToken()) return;
  try {
    const prefs = await requestJson("/api/study/preferences", { method: "GET" }, true);
    applyPrefsToForm(prefs);
  } catch { /* silently ignore */ }
}

// Load preferences on profile page
if (savePrefsBtn || resetPrefsBtn) loadPreferences();

// ═══════════════════════════════════════════════════════════════════════════════
// INITIALIZATION — runs on every authenticated page
// ═══════════════════════════════════════════════════════════════════════════════

// Update auth display
updateAuthState();
populateProfile();

// Restore voice list once DOM + speech API is ready
if (typeof speechSynthesis !== "undefined") {
  if (speechSynthesis.getVoices().length) populateVoiceList();
  else speechSynthesis.onvoiceschanged = populateVoiceList;
}

// Initialize metrics if noteText exists
updateMetrics();

// Initialize level switcher visibility
(function initLevelSwitcher() {
  const levelSwitcher = document.getElementById("levelSwitcher");
  if (levelSwitcher) levelSwitcher.style.display = activeTool === "explain" ? "" : "none";
})();

// Speed slider initial readout
if (speedSlider && speedReadout) {
  speedReadout.textContent = parseFloat(speedSlider.value).toFixed(1) + "x";
}

// (uploadTriggerBtn listener registered at file-upload section above)
