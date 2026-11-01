/**
 * Antara Clinical Intelligence Dashboard Controller
 */

let currentSessionId = "";
let currentReportData = null;
let currentFilter = "all";

document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  
  // Check if loaded with a specific session ID (e.g. from live intake redirect)
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get("session_id");
  if (sessionId) {
    loadLiveSession(sessionId);
  } else {
    // Automatically load the latest intake session stored in memory
    loadLatestSession();
  }
});

function setupEventListeners() {
  // Session JSON file import handler (header & empty-state buttons)
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const sessionObj = JSON.parse(event.target.result);
        await analyzeAndRenderSession(sessionObj);
      } catch (err) {
        alert("Invalid JSON file uploaded: " + err.message);
      }
    };
    reader.readAsText(file);
  };

  const fileInput = document.getElementById("jsonFileInput");
  if (fileInput) fileInput.addEventListener("change", handleFileUpload);

  const fileInputEmpty = document.getElementById("jsonFileInputEmpty");
  if (fileInputEmpty) fileInputEmpty.addEventListener("change", handleFileUpload);

  // PDF Export
  const btnPdf = document.getElementById("btnDownloadPdf");
  if (btnPdf) {
    btnPdf.addEventListener("click", () => {
      if (!currentSessionId) {
        alert("Please load or complete an intake session before exporting PDF.");
        return;
      }
      window.location.href = `/api/report/${encodeURIComponent(currentSessionId)}/pdf`;
    });
  }

  // Data Erasure Execution
  const btnErase = document.getElementById("btnEraseData");
  if (btnErase) {
    btnErase.addEventListener("click", async () => {
      if (!currentSessionId) {
        alert("No active session to erase.");
        return;
      }
      if (!confirm(`Are you sure you want to permanently erase session records for "${currentSessionId}" from active memory?`)) {
        return;
      }
      try {
        const res = await fetch(`/api/erase/${encodeURIComponent(currentSessionId)}`, {
          method: "POST"
        });
        const receipt = await res.json();
        showErasureModal(receipt);
      } catch (err) {
        alert("Erasure failed: " + err.message);
      }
    });
  }

  // Close modal
  const btnCloseModal = document.getElementById("btnCloseModal");
  if (btnCloseModal) {
    btnCloseModal.addEventListener("click", () => {
      document.getElementById("erasureModal").classList.remove("show");
      const pill = document.getElementById("erasureStatusPill");
      pill.textContent = "Data Purged & Zeroed";
      pill.className = "status-pill status-erased";
    });
  }

  // Transcript filters
  const filterButtons = document.querySelectorAll(".filter-btn");
  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      filterButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.getAttribute("data-filter");
      renderTranscriptTable();
    });
  });
}

function showNoSessionCard() {
  const card = document.getElementById("noSessionCard");
  if (card) card.style.display = "block";
}

function hideNoSessionCard() {
  const card = document.getElementById("noSessionCard");
  if (card) card.style.display = "none";
}

async function loadLatestSession() {
  try {
    const res = await fetch("/api/report/latest");
    if (!res.ok) throw new Error("No active session in memory");
    currentReportData = await res.json();
    currentSessionId = currentReportData.metadata.sessionId;
    hideNoSessionCard();
    renderFullDashboard(currentReportData);
  } catch (err) {
    console.log("No recent intake session in memory:", err);
    showNoSessionCard();
  }
}

async function loadLiveSession(sessionId) {
  try {
    const res = await fetch(`/api/report/${encodeURIComponent(sessionId)}`);
    if (!res.ok) throw new Error("Could not fetch session report");
    currentReportData = await res.json();
    currentSessionId = currentReportData.metadata.sessionId;
    hideNoSessionCard();
    renderFullDashboard(currentReportData);
  } catch (err) {
    console.warn("Live session lookup failed:", err);
    loadLatestSession();
  }
}

async function analyzeAndRenderSession(sessionData) {
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sessionData)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Analysis request failed");
    }

    currentReportData = await res.json();
    currentSessionId = currentReportData.metadata.sessionId;
    hideNoSessionCard();
    renderFullDashboard(currentReportData);
  } catch (err) {
    console.error("Analysis failed:", err);
    alert("Analysis failed: " + err.message);
  }
}

    currentReportData = await res.json();
    currentSessionId = currentReportData.metadata.sessionId;
    renderFullDashboard(currentReportData);
  } catch (err) {
    console.error("Analysis failed:", err);
    alert("Analysis failed: " + err.message);
  }
}

function renderFullDashboard(report) {
  const meta = report.metadata;
  const s1 = report.section1_main_concerns;
  const s2 = report.section2_emotions_and_trajectory;
  const s3 = report.section3_themes_and_triggers;
  const s4 = report.section4_clinical_observations;
  const s5 = report.section5_therapy_goals;

  // 1. Client Overview Card
  document.getElementById("clientPseudonym").textContent = `${meta.clientPseudonym} (Client Pseudonym)`;
  document.getElementById("lblSessionId").textContent = meta.sessionId;
  document.getElementById("lblCompletedAt").textContent = meta.completedAt || new Date().toISOString();
  document.getElementById("clientAvatar").textContent = (meta.clientPseudonym || "C").charAt(0).toUpperCase();

  // Reset status pill
  const pill = document.getElementById("erasureStatusPill");
  pill.textContent = "Active Transient Session";
  pill.className = "status-pill status-healthy";

  // Metrics Bar
  const hLevel = s4.hedging_analysis.level;
  const hTotal = s4.hedging_analysis.total_hedges;
  document.getElementById("valHedgingLevel").textContent = hLevel;
  document.getElementById("subHedgingStats").textContent = `${hTotal} minimizing cues (${s4.hedging_analysis.percentage_answers_hedged}% hedged)`;

  const incCount = s4.inconsistencies.total_flags || 0;
  document.getElementById("valInconsistencies").textContent = incCount > 0 ? `${s4.inconsistencies.severity}` : "None";
  document.getElementById("subInconsistencyCount").textContent = `${incCount} flags detected`;

  const editCount = s4.edited_answers.total_edits;
  document.getElementById("valEdits").textContent = editCount;
  document.getElementById("subSanitizationCount").textContent = `${s4.edited_answers.sanitization_count} sanitizations`;

  const skipCount = s4.avoided_topics.total_skipped;
  document.getElementById("valSkips").textContent = skipCount;
  document.getElementById("subSkipCount").textContent = `${skipCount} skipped questions`;

  // 2. Section 1: Concerns Grid
  const concernsGrid = document.getElementById("concernsContainer");
  concernsGrid.innerHTML = "";
  if (s1.verbatim_quotes && s1.verbatim_quotes.length > 0) {
    s1.verbatim_quotes.forEach(q => {
      const card = document.createElement("div");
      card.className = "concern-card";
      card.innerHTML = `
        <div class="concern-stage">Step ${q.step} • ${q.stage.replace(/_/g, ' ')}</div>
        <p class="concern-quote">“${escapeHtml(q.quote)}”</p>
      `;
      concernsGrid.appendChild(card);
    });
  } else {
    concernsGrid.innerHTML = `<div class="text-muted" style="padding:10px">No high-distress verbatim quotes extracted.</div>`;
  }

  // 3. Section 2: Emotional Trajectory
  document.getElementById("arcNarrative").textContent = s2.trajectory_arc_narrative || "N/A";
  document.getElementById("statStartEmotion").textContent = (s2.start_emotion || "N/A").replace(/_/g, ' ').toUpperCase();
  document.getElementById("statEndEmotion").textContent = (s2.end_emotion || "N/A").replace(/_/g, ' ').toUpperCase();
  document.getElementById("statPeakDistress").textContent = s2.peak_distress_stage || "N/A";

  const stepper = document.getElementById("timelineStepper");
  stepper.innerHTML = "";
  (s2.step_timeline || []).forEach(step => {
    const node = document.createElement("div");
    node.className = "timeline-step-node";

    let color = "#0f766e";
    const em = step.primary_emotion;
    if (em.includes("anxiety") || em.includes("panic")) color = "#ef4444";
    else if (em.includes("sadness") || em.includes("despair")) color = "#3b82f6";
    else if (em.includes("overwhelm") || em.includes("burnout")) color = "#8b5cf6";
    else if (em.includes("guilt")) color = "#f59e0b";
    else if (em.includes("hope")) color = "#10b981";
    else if (em.includes("numb")) color = "#64748b";
    else if (em.includes("avoided")) color = "#94a3b8";

    node.innerHTML = `
      <span class="step-num-badge">Step ${step.step}</span>
      <div class="step-stage-name">${escapeHtml(step.stage_label)}</div>
      <span class="step-emotion-pill" style="background:${color}">${escapeHtml(step.primary_emotion.replace(/_/g, ' '))}</span>
      <p class="step-quote-pop">“${escapeHtml(step.summary_quote || '')}”</p>
    `;
    stepper.appendChild(node);
  });

  // 4. Section 3: Themes & Triggers
  const themeContainer = document.getElementById("themeTagsContainer");
  themeContainer.innerHTML = "";
  (s3.primary_themes || []).forEach(th => {
    const span = document.createElement("span");
    span.className = "theme-tag";
    span.textContent = th.name;
    themeContainer.appendChild(span);
  });

  const triggerList = document.getElementById("triggerListContainer");
  triggerList.innerHTML = "";
  if (s3.situational_triggers && s3.situational_triggers.length > 0) {
    s3.situational_triggers.forEach(tr => {
      const li = document.createElement("li");
      li.className = "trigger-item";
      li.innerHTML = `<span>⚡</span> <strong>${escapeHtml(tr.trigger)}</strong> <span class="text-muted">(Context: "${escapeHtml(tr.context)}")</span>`;
      triggerList.appendChild(li);
    });
  } else {
    triggerList.innerHTML = `<li class="trigger-item text-muted">No explicit temporal triggers isolated.</li>`;
  }

  // 5. Section 5: Therapy Goal
  document.getElementById("therapyGoalText").textContent = s5.verbatim_hope || "No explicit therapy goal recorded.";

  // 6. Section 4: Clinical Observations
  renderInconsistencies(s4.inconsistencies);
  renderEdits(s4.edited_answers);
  renderHedging(s4.hedging_analysis);

  // 7. Section 6: Full Transcript
  renderTranscriptTable();
}

function renderInconsistencies(incons) {
  const container = document.getElementById("inconsistencyContent");
  const badge = document.getElementById("badgeInconsistencySev");
  badge.textContent = incons.severity || "None";

  if (!incons.detected || !incons.items || incons.items.length === 0) {
    container.innerHTML = `<p class="obs-interpretation">No overt affective contradictions detected between opening statements and described daily functioning.</p>`;
    return;
  }

  container.innerHTML = "";
  incons.items.forEach(flag => {
    const card = document.createElement("div");
    card.className = "inconsistency-card";
    
    let quotesHtml = "";
    if (flag.primary_statement && flag.contrasting_statement) {
      quotesHtml = `
        <div class="incons-quotes-compare">
          <div>${escapeHtml(flag.primary_statement)}</div>
          <div>${escapeHtml(flag.contrasting_statement)}</div>
        </div>
      `;
    } else if (flag.evidence_quote) {
      quotesHtml = `<div class="incons-quotes-compare"><div>Quote: "${escapeHtml(flag.evidence_quote)}"</div></div>`;
    }

    card.innerHTML = `
      <div class="incons-type">${escapeHtml(flag.type)} (Severity: ${escapeHtml(flag.severity)})</div>
      <div class="incons-expl">${escapeHtml(flag.explanation)}</div>
      ${quotesHtml}
    `;
    container.appendChild(card);
  });
}

function renderEdits(edits) {
  const container = document.getElementById("editsContent");
  const badge = document.getElementById("badgeEditCount");
  badge.textContent = `${edits.total_edits} Revisions`;

  if (!edits.records || edits.records.length === 0) {
    container.innerHTML = `<p class="obs-interpretation">Client submitted responses without retrospective revision.</p>`;
    return;
  }

  container.innerHTML = `<p class="obs-interpretation">${escapeHtml(edits.clinical_takeaway)}</p>`;
  edits.records.forEach(rec => {
    const card = document.createElement("div");
    card.className = "diff-card";
    
    let tagHtml = "";
    if (rec.edit_type === "VULNERABILITY_RETRACTION") {
      tagHtml = `<span class="diff-sanitization-flag">⚠️ ${escapeHtml(rec.edit_type_label)}: Removed "${(rec.removed_vulnerability_terms || []).join(', ')}"</span>`;
    } else if (rec.edit_type === "MINOR_TYPO" || rec.edit_type === "COSMETIC_CASING") {
      tagHtml = `<span class="badge" style="background:#f1f5f9; color:#64748b; font-size:11px; margin-bottom:6px;">ℹ️ ${escapeHtml(rec.edit_type_label)}</span>`;
    } else {
      tagHtml = `<span class="badge" style="background:#e0f2fe; color:#0369a1; font-size:11px; margin-bottom:6px;">🔄 ${escapeHtml(rec.edit_type_label)}</span>`;
    }

    card.innerHTML = `
      <div class="diff-step-title">Step ${rec.step} • ${rec.stage.replace(/_/g, ' ')}</div>
      ${tagHtml}
      <div class="diff-body">${rec.html_diff}</div>
    `;
    container.appendChild(card);
  });
}

function renderHedging(hedging) {
  const list = document.getElementById("hedgingSamplesList");
  document.getElementById("badgeHedgingLevel").textContent = hedging.level;
  document.getElementById("hedgingInterpretation").textContent = hedging.interpretation;

  list.innerHTML = "";
  if (!hedging.highlighted_examples || hedging.highlighted_examples.length === 0) {
    list.innerHTML = `<span class="text-muted">No significant minimizing phrases found.</span>`;
    return;
  }

  hedging.highlighted_examples.forEach(ex => {
    const item = document.createElement("div");
    item.style.marginBottom = "8px";
    item.style.fontSize = "13px";
    item.innerHTML = `
      <strong>Step ${ex.step}:</strong> "${escapeHtml(ex.answer)}"
      <br/><span class="text-muted" style="font-size:11.5px">Matched minimizing phrases: <i>${ex.matched_phrases.join(', ')}</i></span>
    `;
    list.appendChild(item);
  });
}

function renderTranscriptTable() {
  if (!currentReportData) return;
  const rows = currentReportData.section6_attached_transcript || [];
  const tbody = document.getElementById("transcriptTableBody");
  tbody.innerHTML = "";

  const filtered = rows.filter(r => {
    if (currentFilter === "edited") return r.is_edited;
    if (currentFilter === "skipped") return r.is_skipped;
    return true;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `<div style="padding:20px; text-align:center; color:#64748b;">No steps match the selected filter.</div>`;
    return;
  }

  filtered.forEach(item => {
    const row = document.createElement("div");
    row.className = "transcript-row";

    let badgeClass = "badge-verbatim";
    if (item.is_edited) badgeClass = "badge-edited";
    if (item.is_skipped) badgeClass = "badge-skipped";

    let responseHtml = "";
    if (item.is_skipped) {
      responseHtml = `<i style="color:#94a3b8">[Question Skipped by Client]</i>`;
    } else if (item.is_edited && item.original_answer) {
      responseHtml = `
        <div><strong>Final:</strong> ${escapeHtml(item.final_answer)}</div>
        <div style="margin-top:4px; font-size:12px; color:#b91c1c;">
          <strong>Original:</strong> <del>${escapeHtml(item.original_answer)}</del>
        </div>
      `;
    } else {
      responseHtml = `<div>${escapeHtml(item.final_answer || '')}</div>`;
    }

    row.innerHTML = `
      <div class="row-step">Step ${item.step}</div>
      <div class="row-stage">${escapeHtml((item.stage || '').replace(/_/g, ' '))}</div>
      <div class="row-dialogue">
        <strong>Q: ${escapeHtml(item.question)}</strong>
        ${responseHtml}
      </div>
      <div class="row-marker">
        <span class="badge ${badgeClass}">${item.marker}</span>
      </div>
    `;
    tbody.appendChild(row);
  });
}

function showErasureModal(receipt) {
  document.getElementById("auditSessionId").textContent = receipt.sessionId;
  document.getElementById("auditTimestamp").textContent = receipt.erasureTimestamp;
  document.getElementById("auditProofHash").textContent = receipt.auditProofHash;
  document.getElementById("erasureModal").classList.add("show");
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
