/**
 * Antara Patient Intake Application Controller
 */

let sessionState = {
  sessionId: "antara_session_" + Date.now().toString(36),
  startedAt: new Date().toISOString(),
  currentStageIndex: 1, // Stage 2: easy opening
  currentStep: 1,
  transcript: [],
  isCrisisLocked: false,
  editingStepIndex: null
};

const STAGE_TITLES = [
  "Consent & Setting",
  "Initial Check-in",
  "Somatic Sensations",
  "Situations & Triggers",
  "Daily Rhythms & Sleep",
  "Relational Atmosphere",
  "Therapy Aspirations",
  "Gentle Close"
];

document.addEventListener("DOMContentLoaded", () => {
  setupIntakeListeners();
});

function setupIntakeListeners() {
  // Screen 1: Start Button
  const btnStart = document.getElementById("btnStartIntake");
  if (btnStart) {
    btnStart.addEventListener("click", () => {
      // Record consent as Step 1
      sessionState.transcript.push({
        step: 1,
        stage: "1_consent",
        question: "Consent and Confidentiality Agreement",
        finalAnswer: "Client confirmed understanding and provided consent to proceed.",
        originalAnswer: null,
        isEdited: false,
        isSkipped: false,
        timestamp: new Date().toISOString()
      });

      switchScreen("screenChat");
      renderStageDots();
      fetchNextBotQuestion(null, false);
    });
  }

  // Screen 2: Send Answer
  const btnSend = document.getElementById("btnSendAnswer");
  const txtAnswer = document.getElementById("txtAnswer");

  if (btnSend && txtAnswer) {
    btnSend.addEventListener("click", () => handleUserSubmit());
    txtAnswer.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleUserSubmit();
      }
    });
  }

  // Screen 2: Skip Question
  const btnSkip = document.getElementById("btnSkipQuestion");
  if (btnSkip) {
    btnSkip.addEventListener("click", () => handleUserSkip());
  }

  // Edit Modal controls
  const btnCloseEdit = document.getElementById("btnCloseEditModal");
  const btnCancelEdit = document.getElementById("btnCancelEdit");
  const btnSaveEdit = document.getElementById("btnSaveEdit");

  if (btnCloseEdit) btnCloseEdit.addEventListener("click", closeEditModal);
  if (btnCancelEdit) btnCancelEdit.addEventListener("click", closeEditModal);
  if (btnSaveEdit) {
    btnSaveEdit.addEventListener("click", () => saveEditedAnswer());
  }

  // Screen 3: Restart Session
  const btnRestart = document.getElementById("btnRestartSession");
  if (btnRestart) {
    btnRestart.addEventListener("click", () => {
      window.location.reload();
    });
  }
}

function switchScreen(screenId) {
  document.querySelectorAll(".screen-view").forEach(s => s.classList.remove("active"));
  const target = document.getElementById(screenId);
  if (target) target.classList.add("active");
}

function renderStageDots() {
  const container = document.getElementById("stageDots");
  container.innerHTML = "";
  for (let i = 1; i <= 7; i++) {
    const dot = document.createElement("div");
    dot.className = "step-dot";
    if (i === sessionState.currentStageIndex) dot.classList.add("active");
    else if (i < sessionState.currentStageIndex) dot.classList.add("completed");
    container.appendChild(dot);
  }
  const pill = document.getElementById("stageNamePill");
  pill.textContent = STAGE_TITLES[sessionState.currentStageIndex] || "Intake Session";
}

async function handleUserSubmit() {
  if (sessionState.isCrisisLocked) return;

  const txtAnswer = document.getElementById("txtAnswer");
  const answer = txtAnswer.value.trim();
  if (!answer) return;

  txtAnswer.value = "";

  // 1. Check for Crisis Language
  const crisisCheck = await fetch("/api/chat/check-crisis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: answer })
  }).then(r => r.json());

  if (crisisCheck.is_crisis) {
    sessionState.isCrisisLocked = true;
    displayUserBubble(answer, false);
    displayCrisisCard(crisisCheck.safety_response);
    return;
  }

  // 2. Record User Response
  sessionState.currentStep += 1;
  const currentQ = window.activeBotQuestionText || "How are you feeling?";
  const currentStageId = window.activeBotStageId || "2_easy_opening";

  sessionState.transcript.push({
    step: sessionState.currentStep,
    stage: currentStageId,
    question: currentQ,
    finalAnswer: answer,
    originalAnswer: null,
    isEdited: false,
    isSkipped: false,
    timestamp: new Date().toISOString()
  });

  displayUserBubble(answer, false, sessionState.transcript.length - 1);

  // 3. Request Next Question
  sessionState.currentStageIndex += 1;
  renderStageDots();

  if (sessionState.currentStageIndex > 7) {
    finishIntakeSession();
  } else {
    fetchNextBotQuestion(answer, false);
  }
}

function handleUserSkip() {
  if (sessionState.isCrisisLocked) return;

  sessionState.currentStep += 1;
  const currentQ = window.activeBotQuestionText || "Question";
  const currentStageId = window.activeBotStageId || "stage";

  sessionState.transcript.push({
    step: sessionState.currentStep,
    stage: currentStageId,
    question: currentQ,
    finalAnswer: null,
    originalAnswer: null,
    isEdited: false,
    isSkipped: true,
    timestamp: new Date().toISOString()
  });

  displayUserBubble("[Question Skipped]", true, sessionState.transcript.length - 1);

  sessionState.currentStageIndex += 1;
  renderStageDots();

  if (sessionState.currentStageIndex > 7) {
    finishIntakeSession();
  } else {
    fetchNextBotQuestion(null, true);
  }
}

async function fetchNextBotQuestion(lastAnswer, wasSkipped) {
  showTypingIndicator();

  const res = await fetch("/api/chat/next-question", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      current_stage_index: sessionState.currentStageIndex,
      last_answer: lastAnswer,
      skipped: wasSkipped
    })
  }).then(r => r.json());

  hideTypingIndicator();

  window.activeBotQuestionText = res.question;
  window.activeBotStageId = res.stage_id;

  displayBotBubble(res.question);

  if (res.is_final_stage) {
    // Stage 8 closing
    setTimeout(() => {
      finishIntakeSession();
    }, 2500);
  }
}

function displayBotBubble(text) {
  const container = document.getElementById("dialogueContainer");
  const row = document.createElement("div");
  row.className = "message-row bot-row";
  row.innerHTML = `
    <div class="bot-bubble">
      <p class="bot-question-text">${escapeHtml(text)}</p>
    </div>
  `;
  container.appendChild(row);
  scrollToBottom();
}

function displayUserBubble(text, isSkipped, itemIndex) {
  const container = document.getElementById("dialogueContainer");
  const row = document.createElement("div");
  row.className = "message-row user-row";
  row.id = `userMsgRow_${itemIndex}`;

  let contentHtml = `<p class="user-answer-text ${isSkipped ? 'is-skipped' : ''}">${escapeHtml(text)}</p>`;
  let editBtnHtml = "";
  if (!isSkipped) {
    editBtnHtml = `
      <div class="bubble-meta-row">
        <span class="edited-tag" id="editedTag_${itemIndex}" style="display:none;">Edited</span>
        <button class="btn-inline-edit" onclick="openEditModal(${itemIndex})">Edit</button>
      </div>
    `;
  }

  row.innerHTML = `
    <div class="user-bubble">
      ${contentHtml}
      ${editBtnHtml}
    </div>
  `;
  container.appendChild(row);
  scrollToBottom();
}

function showTypingIndicator() {
  const container = document.getElementById("dialogueContainer");
  const typingRow = document.createElement("div");
  typingRow.className = "message-row bot-row";
  typingRow.id = "typingIndicatorRow";
  typingRow.innerHTML = `
    <div class="bot-bubble typing-bubble">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  `;
  container.appendChild(typingRow);
  scrollToBottom();
}

function hideTypingIndicator() {
  const indicator = document.getElementById("typingIndicatorRow");
  if (indicator) indicator.remove();
}

function displayCrisisCard(safetyMessage) {
  const card = document.getElementById("crisisCard");
  const content = document.getElementById("crisisContent");
  content.innerHTML = safetyMessage.replace(/\n\n/g, '<br/><br/>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  card.style.display = "flex";
  document.getElementById("responseDock").style.display = "none";
  scrollToBottom();
}

// Edit Modal Handling
window.openEditModal = function(itemIndex) {
  const record = sessionState.transcript[itemIndex];
  if (!record) return;

  sessionState.editingStepIndex = itemIndex;
  document.getElementById("editModalQuestion").textContent = `“${record.question}”`;
  document.getElementById("txtModalEditAnswer").value = record.finalAnswer || "";
  document.getElementById("editModal").classList.add("show");
};

function closeEditModal() {
  document.getElementById("editModal").classList.remove("show");
  sessionState.editingStepIndex = null;
}

function saveEditedAnswer() {
  const idx = sessionState.editingStepIndex;
  if (idx === null || !sessionState.transcript[idx]) return;

  const newText = document.getElementById("txtModalEditAnswer").value.trim();
  if (!newText) return;

  const item = sessionState.transcript[idx];

  // If first time editing, preserve original answer
  if (!item.isEdited) {
    item.originalAnswer = item.finalAnswer;
    item.isEdited = true;
  }
  item.finalAnswer = newText;

  // Update bubble in DOM
  const row = document.getElementById(`userMsgRow_${idx}`);
  if (row) {
    const textEl = row.querySelector(".user-answer-text");
    if (textEl) textEl.textContent = newText;
    const tag = document.getElementById(`editedTag_${idx}`);
    if (tag) tag.style.display = "inline-block";
  }

  closeEditModal();
}

async function finishIntakeSession() {
  document.getElementById("responseDock").style.display = "none";

  const sessionPayload = {
    sessionId: sessionState.sessionId,
    clientPseudonym: "Client",
    startedAt: sessionState.startedAt,
    completedAt: new Date().toISOString(),
    crisisTriggered: sessionState.isCrisisLocked,
    transcript: sessionState.transcript
  };

  try {
    try {
      localStorage.setItem("antara_active_session", JSON.stringify(sessionPayload));
    } catch(e) {}

    const res = await fetch("/api/chat/finish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sessionPayload)
    }).then(r => r.json());

    switchScreen("screenEnd");
    document.getElementById("endAuditHash").textContent = res.erasure_receipt.auditProofHash || "Verified";
    const reportLink = document.querySelector(".btn-view-report");
    if (reportLink) {
      reportLink.href = `/therapist?session_id=${encodeURIComponent(sessionPayload.sessionId)}`;
    }
  } catch (err) {
    console.error("Error finalizing session:", err);
    switchScreen("screenEnd");
  }
}

function scrollToBottom() {
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
