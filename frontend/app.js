const API_BASE = "http://localhost:8000/api";
const pageFragments = {
  dashboard: "pages/dashboard.html",
  upload: "pages/upload.html",
  metrics: "pages/metrics.html",
  prediction: "pages/prediction.html",
};
const state = {
  session: null,
  uploadPreview: null,
  chart: null,
  currentJob: null,
  currentPage: "dashboard",
};

window.addEventListener("DOMContentLoaded", () => {
  initApp().catch((error) => {
    showToast(error.message || "Initialization failed", true);
    console.error(error);
  });
});

async function initApp() {
  // Initialize particle background
  await initParticles();
  // Load shell components
  await loadShell();
  // Bind navigation
  bindNavigation();
  // Set initial page
  if (!location.hash) {
    location.hash = "#dashboard";
  }
  // Navigate to page
  await navigateTo(location.hash.replace("#", ""));
  // Listen for hash changes
  window.addEventListener("hashchange", () => {
    navigateTo(location.hash.replace("#", ""));
  });
  // Start entrance animations
  gsap.registerPlugin(ScrollTrigger);
  animateEntrance();
}

async function initParticles() {
  const particlesContainer = document.getElementById("particles-bg");
  if (particlesContainer && typeof tsParticles !== "undefined") {
    try {
      await tsParticles.load("particles-bg", {
        background: { color: "transparent" },
        fpsLimit: 60,
        interactivity: {
          events: {
            onHover: { enable: true, mode: "repulse" },
            resize: true,
          },
          modes: { repulse: { distance: 150, duration: 0.4 } },
        },
        particles: {
          color: { value: ["#06b6d4", "#8b5cf6", "#10b981"] },
          links: {
            color: "rgba(6, 182, 212, 0.15)",
            distance: 120,
            enable: true,
            opacity: 0.4,
          },
          move: { direction: "none", enable: true, outModes: "bounce", random: true, speed: 0.8, straight: false },
          number: { density: { enable: true, value_area: 1000 }, value: 45 },
          opacity: { value: 0.25 },
          shape: { type: "circle" },
          size: { value: { min: 1, max: 2.5 } },
        },
      });
    } catch (error) {
      console.warn("Particles initialization failed:", error);
    }
  }
}

function animateEntrance() {
  const tl = gsap.timeline();
  tl.to(".sidebar-wrapper", { opacity: 1, duration: 0.6, ease: "power2.out" }, 0)
    .to(".navbar-wrapper", { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }, 0.1)
    .to(".page-container", { opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }, 0.2);
}

async function loadShell() {
  const sidebarRoot = document.getElementById("sidebar-root");
  const navbarRoot = document.getElementById("navbar-root");
  sidebarRoot.innerHTML = await fetchText("components/sidebar.html");
  navbarRoot.innerHTML = await fetchText("components/navbar.html");
  
  const refreshButton = document.getElementById("refresh-session");
  refreshButton?.addEventListener("click", async () => {
    // Show active state on refresh icon rotating
    const svg = refreshButton.querySelector("svg");
    if (svg) gsap.to(svg, { rotate: "+=360", duration: 0.5, ease: "power2.inOut" });
    
    await refreshSession()
      .then(() => showToast("Session synchronized with backend.", false))
      .catch((error) => showToast(error.message, true));
  });

  const resetButton = document.getElementById("reset-session");
  resetButton?.addEventListener("click", async () => {
    const doubleCheck = confirm("CAUTION: Are you sure you want to reset the entire AutoML studio workspace?\nThis will purge all datasets, trained models, metrics, and report files from the system.");
    if (doubleCheck) {
      await resetWorkspace().catch((error) => showToast(error.message, true));
    }
  });

  // Re-run connection check initially
  await checkHealth();
}

async function checkHealth() {
  try {
    await apiFetch("/health");
    updateApiStatus(true);
  } catch {
    updateApiStatus(false);
  }
}

function updateApiStatus(isOnline) {
  const dot = document.getElementById("connection-status-dot");
  const text = document.getElementById("connection-status-text");
  const navPulse = document.getElementById("navbar-api-pulse");
  
  if (isOnline) {
    if (dot) dot.className = "status-dot bg-cyan-400 animate-pulse";
    if (text) {
      text.textContent = "API ACTIVE";
      text.className = "nav-label font-mono text-[10px] tracking-wider text-cyan-400";
    }
    if (navPulse) navPulse.className = "w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse block";
  } else {
    if (dot) dot.className = "status-dot bg-red-500";
    if (text) {
      text.textContent = "API OFFLINE";
      text.className = "nav-label font-mono text-[10px] tracking-wider text-red-500 font-bold";
    }
    if (navPulse) navPulse.className = "w-1.5 h-1.5 rounded-full bg-red-500 block";
  }
}

function bindNavigation() {
  document.body.addEventListener("click", (event) => {
    const target = event.target.closest("[data-page]");
    if (!target) return;
    event.preventDefault();
    const page = target.dataset.page;
    if (page) {
      location.hash = `#${page}`;
    }
  });
}

async function navigateTo(page) {
  const normalizedPage = page in pageFragments ? page : "dashboard";
  state.currentPage = normalizedPage;
  updateActiveLink(normalizedPage);
  await loadPage(normalizedPage);
}

function updateActiveLink(page) {
  document.querySelectorAll(".nav-item").forEach((link) => {
    link.classList.toggle("active", link.dataset.page === page);
  });
}

async function loadPage(page) {
  const pageContent = document.getElementById("page-content");
  
  // Transition page slide out
  await gsap.to(pageContent, { opacity: 0, y: -10, duration: 0.15, ease: "power2.in" });
  
  pageContent.innerHTML = await fetchText(pageFragments[page]);
  updatePageTitle(page);
  
  // Initialize page-specific listeners BEFORE loading session values, 
  // so elements exist to be updated when refreshSession executes!
  if (page === "dashboard") initDashboardPage();
  if (page === "upload") initUploadPage();
  if (page === "metrics") initMetricsPage();
  if (page === "prediction") initPredictionPage();
  
  await refreshSession();
  
  // Transition page slide in
  gsap.fromTo(
    pageContent, 
    { opacity: 0, y: 15 },
    { opacity: 1, y: 0, duration: 0.35, ease: "power2.out", delay: 0.05 }
  );
  
  // Animate metric cards staggered
  animateMetricCards();
}

function updatePageTitle(page) {
  const titles = {
    dashboard: ["Dashboard Home", "Monitor dataset health, training status, and model results at a glance."],
    upload: ["Upload & Train", "Prepare a dataset, train the best models, and monitor progress."],
    metrics: ["Metrics Dashboard", "Review model performance, leaderboard, and report artifacts."],
    prediction: ["Prediction Studio", "Run batch inference with your chosen trained model."],
  };
  const [pageTitle, pageSubtitle] = titles[page] || titles.dashboard;
  const titleEl = document.getElementById("page-title");
  const subtitleEl = document.getElementById("page-subtitle");
  if (titleEl) titleEl.textContent = pageTitle;
  if (subtitleEl) subtitleEl.textContent = pageSubtitle;
}

async function refreshSession() {
  try {
    state.session = await apiFetch("/session");
    updateApiStatus(true);
    
    if (state.currentPage === "upload") {
      renderUploadSummary();
    }
    if (state.currentPage === "dashboard") {
      renderDashboardPage();
    }
    if (state.currentPage === "metrics") {
      renderMetricsPage();
    }
    if (state.currentPage === "prediction") {
      renderPredictionControls();
    }
    return state.session;
  } catch (error) {
    updateApiStatus(false);
    throw error;
  }
}

async function resetWorkspace() {
  const loader = document.getElementById("loading-overlay");
  if (loader) loader.classList.remove("hidden");
  
  try {
    const payload = await apiFetch("/reset", { method: "POST" });
    state.session = null;
    state.uploadPreview = null;
    state.currentJob = null;
    
    if (state.chart) {
      state.chart.destroy();
      state.chart = null;
    }
    
    showToast(`Workspace reset completed. Purged ${payload.removed_files} artifact files.`, false);
    
    // Redirect to dashboard hash
    location.hash = "#dashboard";
    await refreshSession();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (loader) loader.classList.add("hidden");
  }
}

async function initUploadPage() {
  const uploadInput = document.getElementById("upload-input");
  const uploadSelect = document.getElementById("upload-select");
  const dropzone = document.getElementById("upload-dropzone");
  const detectButton = document.getElementById("detect-task-button");
  const prepareButton = document.getElementById("prepare-button");
  const trainButton = document.getElementById("train-button");
  const evaluateButton = document.getElementById("evaluate-button");

  uploadSelect?.addEventListener("click", (e) => {
    e.preventDefault();
    uploadInput?.click();
  });
  
  uploadInput?.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (file) await uploadFile(file);
  });
  
  dropzone?.addEventListener("click", (e) => {
    // Make sure we only click if not clicking the button itself
    if (e.target !== uploadSelect) {
      uploadInput?.click();
    }
  });
  
  dropzone?.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropzone.classList.add("dragover");
  });
  
  dropzone?.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });
  
  dropzone?.addEventListener("drop", async (event) => {
    event.preventDefault();
    dropzone.classList.remove("dragover");
    const file = event.dataTransfer?.files?.[0];
    if (file) await uploadFile(file);
  });

  detectButton?.addEventListener("click", async () => {
    await detectTask().catch((error) => showToast(error.message, true));
  });
  
  prepareButton?.addEventListener("click", async () => {
    await prepareData().catch((error) => showToast(error.message, true));
  });
  
  trainButton?.addEventListener("click", async () => {
    await trainModels().catch((error) => showToast(error.message, true));
  });
  
  evaluateButton?.addEventListener("click", async () => {
    await evaluateModels().catch((error) => showToast(error.message, true));
  });

  // Enable stepper nodes navigation if completed/active
  setupStepperInteractiveClicks();
}

function setupStepperInteractiveClicks() {
  const stepperSteps = document.querySelectorAll(".stepper-step");
  stepperSteps.forEach((stepNode) => {
    stepNode.addEventListener("click", () => {
      const stepNum = parseInt(stepNode.dataset.step);
      // Determine what sections are available based on session
      const session = state.session;
      if (!session) return;
      
      // Let users click to scroll to the corresponding section if that step is completed or active
      if (stepNode.classList.contains("active") || stepNode.classList.contains("completed")) {
        let targetId = "";
        if (stepNum === 1) targetId = "section-upload";
        else if (stepNum === 2) targetId = "section-profile";
        else if (stepNum === 3) targetId = "section-profile"; // profile card contains prep button
        else if (stepNum === 4) targetId = "section-train-controls";
        else if (stepNum === 5) targetId = "section-terminal"; // terminal has evaluation triggers
        
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
          targetEl.scrollIntoView({ behavior: "smooth", block: "center" });
          gsap.fromTo(targetEl, { boxShadow: "0 0 0px rgba(139, 92, 246, 0)" }, { boxShadow: "0 0 20px rgba(139, 92, 246, 0.25)", duration: 0.8, yoyo: true, repeat: 1 });
        }
      } else {
        showToast(`Step ${stepNum} is locked. Complete the preceding stages first.`, true);
      }
    });
  });
}

function updateStepper(step) {
  const stepperProgress = document.getElementById("stepper-progress");
  if (!stepperProgress) return;
  
  const progressWidths = {
    1: "0%",
    2: "25%",
    3: "50%",
    4: "75%",
    5: "100%"
  };
  stepperProgress.style.width = progressWidths[step] || "0%";
  
  for (let i = 1; i <= 5; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    if (!stepEl) continue;
    
    if (i < step) {
      stepEl.classList.remove("active");
      stepEl.classList.add("completed");
    } else if (i === step) {
      stepEl.classList.add("active");
      stepEl.classList.remove("completed");
    } else {
      stepEl.classList.remove("active");
      stepEl.classList.remove("completed");
    }
  }
}

async function uploadFile(file) {
  if (!file.name.toLowerCase().endsWith(".csv")) {
    showToast("Please upload a CSV formatted dataset.", true);
    return;
  }
  const form = new FormData();
  form.append("file", file);
  
  const loader = document.getElementById("loading-overlay");
  if (loader) loader.classList.remove("hidden");

  try {
    const payload = await apiFetch("/upload", { method: "POST", body: form });
    state.uploadPreview = payload.preview || [];
    state.session = {
      ...state.session,
      has_dataset: true,
      dataset: {
        filename: payload.filename,
        n_rows: payload.n_rows,
        n_cols: payload.n_cols,
        columns: payload.columns,
      },
    };
    renderUploadSummary(payload);
    showToast(`Dataset '${payload.filename}' loaded successfully.`, false);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (loader) loader.classList.add("hidden");
  }
}

async function detectTask() {
  const target = document.getElementById("target-column")?.value.trim() || null;
  const taskHint = document.getElementById("task-hint")?.value.trim() || null;
  
  const loader = document.getElementById("loading-overlay");
  if (loader) loader.classList.remove("hidden");

  try {
    const payload = await apiFetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target, task_hint: taskHint || null }),
    });
    state.session = {
      ...state.session,
      task: payload,
    };
    await fetchCandidateModels();
    showToast("Task identified & ML algorithms suggested.", false);
    renderUploadSummary();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (loader) loader.classList.add("hidden");
  }
}

async function fetchCandidateModels() {
  const payload = await apiFetch("/select-models", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ overrides: null }),
  });
  state.session = {
    ...state.session,
    selected_models: payload.candidates.map((candidate) => candidate.name),
  };
  showModelCandidates(payload.candidates);
}

async function prepareData() {
  const dropDuplicates = document.getElementById("clean-drop-duplicates")?.checked ?? true;
  const imputeNumeric = document.getElementById("clean-impute-numeric")?.value ?? "median";
  const imputeCategorical = document.getElementById("clean-impute-categorical")?.value ?? "most_frequent";
  const scaleNumeric = document.getElementById("clean-scale-numeric")?.checked ?? true;

  const body = {
    drop_duplicates: dropDuplicates,
    impute_strategy_numeric: imputeNumeric,
    impute_strategy_categorical: imputeCategorical,
    scale_numeric: scaleNumeric,
  };
  
  const loader = document.getElementById("loading-overlay");
  if (loader) loader.classList.remove("hidden");

  try {
    const payload = await apiFetch("/prepare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    state.session = {
      ...state.session,
      preparation: payload,
    };
    showToast("Data cleaning and features scaled successfully.", false);
    renderUploadSummary();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (loader) loader.classList.add("hidden");
  }
}

async function trainModels() {
  const testSizeVal = document.getElementById("train-test-size")?.value;
  const testSize = testSizeVal ? parseFloat(testSizeVal) : 0.2;
  
  const loader = document.getElementById("loading-overlay");
  if (loader) loader.classList.remove("hidden");

  try {
    const payload = await apiFetch("/train", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ test_size: testSize, random_seed: 42 }),
    });
    
    state.currentJob = payload.job_id;
    
    // Immediately show execution panels
    document.getElementById("section-terminal")?.classList.remove("hidden");
    
    updateTrainingStatus({ job_id: payload.job_id, state: "PENDING", progress: 0 });
    showToast("AutoML model sweep pipeline job launched.", false);
    pollTrainingStatus(payload.job_id);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (loader) loader.classList.add("hidden");
  }
}

async function evaluateModels() {
  const loader = document.getElementById("loading-overlay");
  if (loader) loader.classList.remove("hidden");

  try {
    const payload = await apiFetch("/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    state.session = {
      ...state.session,
      evaluation: payload,
      best_model: payload.best_model,
    };
    showToast(`Leaderboard built. Best model: ${payload.best_model}`, false);
    
    // Redirect to metrics page to show off evaluation scores
    setTimeout(() => {
      location.hash = "#metrics";
    }, 1000);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (loader) loader.classList.add("hidden");
  }
}

async function pollTrainingStatus(jobId) {
  try {
    const status = await apiFetch(`/train/status/${jobId}`);
    updateTrainingStatus(status);
    appendTrainingLog(status);
    
    if (status.state === "PENDING" || status.state === "RUNNING") {
      setTimeout(() => pollTrainingStatus(jobId), 2000);
      return;
    }
    
    // If completed or failed, synchronize the session state
    await refreshSession();
    
    if (status.state === "COMPLETED") {
      showToast("AutoML engine pipeline finished sweeps successfully.", false);
    }
    if (status.error) {
      showToast(`Training Job Error: ${status.error}`, true);
    }
  } catch (error) {
    showToast(error.message, true);
  }
}

function updateTrainingStatus(status) {
  const jobIdEl = document.getElementById("training-job-id");
  const stateEl = document.getElementById("training-state");
  const progressEl = document.getElementById("training-progress");
  
  if (jobIdEl) jobIdEl.textContent = status.job_id || "none";
  if (stateEl) {
    stateEl.textContent = status.state || "idle";
    stateEl.className = "text-[10px] px-2 py-0.5 border rounded font-mono font-semibold";
    if (status.state === "COMPLETED") {
      stateEl.classList.add("bg-emerald-500/10", "border-emerald-500/30", "text-emerald-400");
    } else if (status.state === "FAILED" || status.error) {
      stateEl.classList.add("bg-red-500/10", "border-red-500/30", "text-red-400");
    } else if (status.state === "RUNNING" || status.state === "PENDING") {
      stateEl.classList.add("bg-amber-500/10", "border-amber-500/30", "text-amber-400", "animate-pulse");
    } else {
      stateEl.classList.add("bg-slate-900", "border-white/10", "text-slate-400");
    }
  }
  if (progressEl) progressEl.textContent = `${status.progress ?? 0}%`;
}

function appendTrainingLog(status) {
  const log = document.getElementById("training-log");
  if (!log) return;
  
  log.innerHTML = "";
  const modelRows = status.models || [];
  
  modelRows.forEach((model) => {
    const item = document.createElement("div");
    item.className = "log-line py-1 border-b border-white/[0.02] last:border-0 font-mono text-xs flex justify-between items-center";
    
    let statusClass = "text-slate-400";
    if (model.state === "COMPLETED") statusClass = "text-emerald-400 font-semibold";
    else if (model.state === "RUNNING") statusClass = "text-amber-400 animate-pulse";
    else if (model.state === "FAILED") statusClass = "text-red-400 font-bold";
    else if (model.state === "PENDING") statusClass = "text-slate-500";
    
    const duration = model.duration_seconds ? ` (${model.duration_seconds.toFixed(1)}s)` : "";
    const errText = model.error ? ` <span class="text-red-500 block text-[10px] mt-0.5">${model.error}</span>` : "";
    
    item.innerHTML = `
      <div>
        <span class="text-slate-300">${model.name}</span>
        ${errText}
      </div>
      <div class="flex items-center gap-2">
        <span class="${statusClass}">${model.state}</span>
        <span class="text-slate-500 text-[10px]">${duration}</span>
      </div>
    `;
    log.appendChild(item);
  });
  
  if (status.error) {
    const errDiv = document.createElement("div");
    errDiv.className = "text-red-400 font-mono text-xs mt-3 p-2 bg-red-950/20 border border-red-500/20 rounded";
    errDiv.innerHTML = `<strong>Engine Error:</strong> ${status.error}`;
    log.appendChild(errDiv);
  }
  
  if (!modelRows.length && !status.error) {
    log.innerHTML = `<div class="text-slate-500 font-mono text-xs animate-pulse">Initializing training sequence...</div>`;
  }
  
  // Auto scroll to bottom
  log.scrollTop = log.scrollHeight;
}

function renderUploadSummary(uploadPayload) {
  const session = state.session;
  const dataset = session?.dataset;
  
  const statusLabel = document.getElementById("dataset-status");
  const rowsLabel = document.getElementById("dataset-rows");
  const colsLabel = document.getElementById("dataset-cols");
  
  const detectButton = document.getElementById("detect-task-button");
  const prepareButton = document.getElementById("prepare-button");
  const trainButton = document.getElementById("train-button");
  const evaluateButton = document.getElementById("evaluate-button");
  
  const sectionTrainControls = document.getElementById("section-train-controls");
  const sectionTerminal = document.getElementById("section-terminal");
  
  if (uploadPayload) {
    if (statusLabel) statusLabel.textContent = uploadPayload.filename;
    if (rowsLabel) rowsLabel.textContent = String(uploadPayload.n_rows);
    if (colsLabel) colsLabel.textContent = String(uploadPayload.n_cols);
    renderPreviewTable(uploadPayload.preview);
    const indicator = document.getElementById("preview-row-indicator");
    if (indicator) indicator.textContent = `${uploadPayload.n_rows} rows loaded`;
  } else if (dataset) {
    if (statusLabel) statusLabel.textContent = dataset.filename || "Dataset loaded";
    if (rowsLabel) rowsLabel.textContent = String(dataset.n_rows || "-");
    if (colsLabel) colsLabel.textContent = String(dataset.n_cols || "-");
    const indicator = document.getElementById("preview-row-indicator");
    if (indicator) indicator.textContent = `${dataset.n_rows || 0} rows loaded`;
    if (state.uploadPreview) {
      renderPreviewTable(state.uploadPreview);
    }
  } else {
    if (statusLabel) statusLabel.textContent = "-";
    if (rowsLabel) rowsLabel.textContent = "-";
    if (colsLabel) colsLabel.textContent = "-";
    const indicator = document.getElementById("preview-row-indicator");
    if (indicator) indicator.textContent = "Awaiting upload...";
    renderPreviewTable([]);
  }

  // Determine current active step
  let activeStep = 1; // Step 1: Upload
  
  if (session?.has_dataset) {
    activeStep = 2; // Step 2: Profile
  }
  if (session?.task) {
    activeStep = 3; // Step 3: Prepare
    showAnalysisCard(session.task);
  }
  if (session?.preparation) {
    activeStep = 4; // Step 4: Train
  }
  if (session?.last_job && session.last_job.state === "COMPLETED") {
    activeStep = 5; // Step 5: Evaluate
  }
  
  updateStepper(activeStep);

  // Enable/Disable buttons & Show/Hide sections
  if (detectButton) detectButton.disabled = activeStep < 2;
  if (prepareButton) prepareButton.disabled = activeStep < 3;
  if (trainButton) trainButton.disabled = activeStep < 4;
  
  if (activeStep >= 3) {
    sectionTrainControls?.classList.remove("hidden");
  } else {
    sectionTrainControls?.classList.add("hidden");
  }
  
  if (session?.selected_models?.length) {
    showSelectedModelBadges(session.selected_models);
  }

  const lastJob = session?.last_job;
  if (lastJob) {
    sectionTerminal?.classList.remove("hidden");
    updateTrainingStatus(lastJob);
    appendTrainingLog(lastJob);
    
    // Check if training job is running in background and not yet tracked in app lifecycle
    if ((lastJob.state === "PENDING" || lastJob.state === "RUNNING") && state.currentJob !== lastJob.job_id) {
      state.currentJob = lastJob.job_id;
      pollTrainingStatus(lastJob.job_id);
    }
    
    // Show evaluation button if training finished and not yet evaluated
    if (lastJob.state === "COMPLETED") {
      if (evaluateButton) {
        evaluateButton.classList.remove("hidden");
        evaluateButton.disabled = false;
      }
    } else {
      evaluateButton?.classList.add("hidden");
    }
  } else {
    sectionTerminal?.classList.add("hidden");
    evaluateButton?.classList.add("hidden");
  }

  if (session?.evaluation) {
    // If evaluated, show complete step 5
    const step5 = document.getElementById("step-5");
    if (step5) {
      step5.classList.remove("active");
      step5.classList.add("completed");
    }
    const stepperProgress = document.getElementById("stepper-progress");
    if (stepperProgress) stepperProgress.style.width = "100%";
    
    if (evaluateButton) {
      evaluateButton.classList.add("hidden"); // hide since evaluation is done
    }
  }
}

function showSelectedModelBadges(models) {
  const badgeWrapper = document.getElementById("model-candidates");
  if (!badgeWrapper) return;
  badgeWrapper.innerHTML = "";
  models.forEach((name) => {
    const badge = document.createElement("span");
    badge.className = "inline-block bg-violet-950/30 text-violet-400 border border-violet-500/20 px-2.5 py-0.5 rounded text-[10px] font-mono mr-1 mb-1 font-semibold";
    badge.textContent = name;
    badgeWrapper.appendChild(badge);
  });
}

function showAnalysisCard(taskData) {
  const analysisCard = document.getElementById("analysis-card");
  if (!analysisCard) return;
  analysisCard.classList.remove("hidden");
  
  const taskEl = document.getElementById("analysis-task");
  const confidenceEl = document.getElementById("analysis-confidence");
  const targetEl = document.getElementById("analysis-target");
  const featuresEl = document.getElementById("analysis-features");
  
  if (taskEl) taskEl.textContent = taskData.task_type || "-";
  if (confidenceEl) {
    const conf = taskData.confidence;
    confidenceEl.textContent = typeof conf === "number" 
      ? (conf <= 1 ? `${(conf * 100).toFixed(0)}%` : `${conf}%`)
      : "-";
  }
  if (targetEl) targetEl.textContent = taskData.target || "-";
  
  const features = [
    ...(taskData.feature_columns || []),
    taskData.text_column || "",
    taskData.datetime_column || "",
  ]
    .filter(Boolean)
    .join(", ");
  
  if (featuresEl) featuresEl.textContent = features || "-";
}

function showModelCandidates(candidates) {
  const badgeWrapper = document.getElementById("model-candidates");
  if (!badgeWrapper) return;
  badgeWrapper.innerHTML = "";
  candidates?.forEach((candidate) => {
    const badge = document.createElement("span");
    badge.className = "inline-block bg-cyan-950/30 text-cyan-400 border border-cyan-500/20 px-2.5 py-0.5 rounded text-[10px] font-mono mr-1 mb-1 font-semibold";
    badge.textContent = candidate.name;
    badgeWrapper.appendChild(badge);
  });
}

function renderPreviewTable(previewRows) {
  const wrapper = document.getElementById("preview-table-wrapper");
  if (!wrapper) return;
  
  if (!previewRows || !previewRows.length) {
    wrapper.innerHTML = `<span class="text-xs text-slate-500 font-mono">No active dataset preview. Upload a CSV to begin.</span>`;
    return;
  }
  
  const columns = Object.keys(previewRows[0]);
  const table = document.createElement("table");
  table.className = "data-table w-full text-left text-xs font-mono border-collapse";
  
  table.innerHTML = `
    <thead>
      <tr class="border-b border-white/10 text-slate-400 bg-white/[0.01]">
        ${columns.map((header) => `<th class="py-2 px-3 font-semibold text-slate-300 border-r border-white/5 last:border-0">${header}</th>`).join("")}
      </tr>
    </thead>
    <tbody>
      ${previewRows
        .map(
          (row) =>
            `<tr class="border-b border-white/5 hover:bg-white/[0.01]">
              ${columns.map((col) => `<td class="py-2 px-3 border-r border-white/5 last:border-0 text-slate-400 max-w-[150px] truncate" title="${String(row[col] ?? "")}">${String(row[col] ?? "").replace(/\n/g, " ")}</td>`).join("")}
            </tr>`
        )
        .join("")}
    </tbody>
  `;
  
  wrapper.innerHTML = "";
  wrapper.appendChild(table);
}

function initDashboardPage() {
  renderDashboardPage();
}

function renderDashboardPage() {
  const summary = state.session;
  const dataset = summary?.dataset;
  const evaluation = summary?.evaluation;
  const lastJob = summary?.last_job;
  
  const datasetNameEl = document.getElementById("dashboard-dataset-name");
  const rowCountEl = document.getElementById("dashboard-row-count");
  const colCountEl = document.getElementById("dashboard-col-count");
  const taskTypeEl = document.getElementById("dashboard-task-type");
  const taskTargetEl = document.getElementById("dashboard-task-target");
  const bestModelEl = document.getElementById("dashboard-best-model");
  const trainStateEl = document.getElementById("dashboard-train-state");
  const trainProgressEl = document.getElementById("dashboard-train-progress");
  const modelCountEl = document.getElementById("dashboard-model-count");

  if (datasetNameEl) datasetNameEl.textContent = dataset?.filename || "No dataset uploaded";
  if (rowCountEl) rowCountEl.textContent = dataset?.n_rows ? dataset.n_rows.toLocaleString() : "-";
  if (colCountEl) colCountEl.textContent = dataset?.n_cols ? dataset.n_cols.toString() : "-";
  if (taskTypeEl) {
    taskTypeEl.textContent = summary?.task?.task_type || "Awaiting Data";
    taskTypeEl.className = summary?.task?.task_type 
      ? "metric-value text-2xl mt-1 text-slate-100 font-bold capitalize text-gradient bg-clip-text text-transparent bg-gradient-to-r from-violet-400 to-cyan-400" 
      : "metric-value text-2xl mt-1 text-slate-500 font-bold";
  }
  if (taskTargetEl) taskTargetEl.textContent = summary?.task?.target || "-";
  if (bestModelEl) {
    bestModelEl.textContent = summary?.best_model || "None Swept Yet";
    bestModelEl.className = summary?.best_model 
      ? "metric-value text-lg mt-2 truncate text-emerald-400 font-bold" 
      : "metric-value text-lg mt-2 truncate text-slate-500 font-bold";
  }
  if (trainStateEl) {
    trainStateEl.textContent = lastJob?.state || "idle";
    trainStateEl.className = "metric-value text-2xl mt-1 font-bold uppercase tracking-wide font-mono";
    if (lastJob?.state === "RUNNING" || lastJob?.state === "PENDING") {
      trainStateEl.classList.add("text-amber-400", "animate-pulse");
    } else if (lastJob?.state === "COMPLETED") {
      trainStateEl.classList.add("text-emerald-400");
    } else if (lastJob?.state === "FAILED") {
      trainStateEl.classList.add("text-red-400");
    } else {
      trainStateEl.classList.add("text-slate-500");
    }
  }
  if (trainProgressEl) trainProgressEl.textContent = `${lastJob?.progress ?? 0}%`;
  if (modelCountEl) modelCountEl.textContent = String(summary?.evaluation?.evaluations?.length || 0);
  
  renderDashboardChart(evaluation);
}

function getChartGradient(ctx, colorStart, colorEnd) {
  const gradient = ctx.createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0, colorStart);
  gradient.addColorStop(1, colorEnd);
  return gradient;
}

function renderDashboardChart(evaluation) {
  const canvas = document.getElementById("dashboard-chart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  
  const evaluations = evaluation?.evaluations || [];
  if (!evaluations.length) {
    if (state.chart) {
      state.chart.destroy();
      state.chart = null;
    }
    canvas.style.display = "none";
    let placeholder = document.getElementById("dashboard-chart-placeholder");
    if (!placeholder) {
      placeholder = document.createElement("div");
      placeholder.id = "dashboard-chart-placeholder";
      placeholder.className = "text-xs text-slate-500 font-mono text-center py-20 bg-slate-950/20 rounded-md border border-dashed border-white/5";
      placeholder.textContent = "Awaiting model evaluation data to render comparison chart.";
      canvas.parentNode.appendChild(placeholder);
    } else {
      placeholder.style.display = "block";
    }
    return;
  }
  
  canvas.style.display = "block";
  const placeholder = document.getElementById("dashboard-chart-placeholder");
  if (placeholder) placeholder.style.display = "none";

  const labels = evaluations.map((item) => item.name);
  const values = evaluations.map((item) => choosePrimaryMetric(item.metrics, evaluation?.primary_metric));
  
  const primaryMetric = evaluation?.primary_metric || "score";
  const barGradient = getChartGradient(ctx, "rgba(6, 182, 212, 0.85)", "rgba(139, 92, 246, 0.15)");
  const borderGradient = getChartGradient(ctx, "rgba(6, 182, 212, 1)", "rgba(139, 92, 246, 0.7)");

  const data = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: barGradient,
        borderColor: borderGradient,
        borderWidth: 1.5,
        borderRadius: 5,
        hoverBackgroundColor: getChartGradient(ctx, "rgba(6, 182, 212, 1)", "rgba(139, 92, 246, 0.35)"),
        hoverBorderColor: "#ffffff",
      },
    ],
  };

  const config = {
    type: "bar",
    data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { 
            color: "#94a3b8",
            font: { family: "'Fira Code', monospace", size: 10 }
          },
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          border: { dash: [5, 5] }
        },
        x: {
          ticks: { 
            color: "#94a3b8",
            font: { family: "'Space Grotesk', sans-serif", size: 11 }
          },
          grid: { display: false },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(9, 9, 11, 0.95)",
          titleColor: "#ffffff",
          bodyColor: "#06b6d4",
          borderColor: "rgba(255, 255, 255, 0.08)",
          borderWidth: 1,
          padding: 10,
          titleFont: { family: "'Space Grotesk', sans-serif", size: 12 },
          bodyFont: { family: "'Fira Code', monospace", size: 11 },
          cornerRadius: 6,
          displayColors: false,
          callbacks: {
            label: function(context) {
              return ` ${primaryMetric.toUpperCase()}: ${context.parsed.y.toFixed(4)}`;
            }
          }
        },
      },
    },
  };
  
  if (state.chart) {
    state.chart.destroy();
  }
  state.chart = new Chart(canvas, config);
}

async function initMetricsPage() {
  const reportButton = document.getElementById("generate-report-button");
  reportButton?.addEventListener("click", async () => {
    await generateReport().catch((error) => showToast(error.message, true));
  });
  await renderMetricsPage();
}

async function renderMetricsPage() {
  const session = state.session;
  const evaluation = session?.evaluation;
  const hasEvaluation = Boolean(evaluation?.evaluations?.length);
  const bestModel = evaluation?.best_model || "-";
  
  const bestModelEl = document.getElementById("metrics-best-model");
  const accuracyEl = document.getElementById("metrics-accuracy");
  const modelCountEl = document.getElementById("metrics-model-count");
  
  if (bestModelEl) bestModelEl.textContent = bestModel;
  if (accuracyEl) {
    if (evaluation?.primary_metric) {
      const bestEval = evaluation.evaluations.find(e => e.name === bestModel);
      const score = bestEval ? choosePrimaryMetric(bestEval.metrics, evaluation.primary_metric) : null;
      accuracyEl.textContent = score !== null ? `${formatNumber(score)} (${evaluation.primary_metric})` : evaluation.primary_metric;
    } else {
      accuracyEl.textContent = "-";
    }
  }
  if (modelCountEl) modelCountEl.textContent = String(evaluation?.evaluations?.length || 0);

  const listRoot = document.getElementById("leaderboard-list-root");
  if (listRoot) {
    const table = listRoot.querySelector("table");
    const placeholder = listRoot.querySelector("div");
    const tableBody = document.getElementById("leaderboard-body");
    
    if (hasEvaluation) {
      if (table) table.classList.remove("hidden");
      if (placeholder) placeholder.style.display = "none";
      if (tableBody) {
        tableBody.innerHTML = "";
        
        const sortedEvals = [...evaluation.evaluations].sort((a, b) => {
          const valA = choosePrimaryMetric(a.metrics, evaluation.primary_metric);
          const valB = choosePrimaryMetric(b.metrics, evaluation.primary_metric);
          return evaluation.higher_is_better ? valB - valA : valA - valB;
        });

        sortedEvals.forEach((item, index) => {
          const primaryValue = choosePrimaryMetric(item.metrics, evaluation.primary_metric);
          const row = document.createElement("tr");
          row.className = "border-b border-white/5 hover:bg-white/[0.01] transition-colors";
          
          const otherMetrics = Object.entries(item.metrics)
            .map(([key, value]) => `<span class="inline-block bg-white/[0.04] px-2 py-0.5 rounded text-[10px] text-slate-400 mr-1.5 mb-1.5 font-mono">${key}: ${formatNumber(value)}</span>`)
            .join("");

          const rankBadge = index === 0 
            ? `<span class="text-amber-400 mr-2">🏆</span>` 
            : `<span class="text-slate-500 mr-2.5 font-mono w-4 inline-block text-center">#${index + 1}</span>`;

          row.innerHTML = `
            <td class="py-3 px-2 font-medium flex items-center">
              ${rankBadge}
              <span class="${index === 0 ? "text-emerald-400 font-bold" : "text-slate-200"}">${item.name}</span>
            </td>
            <td class="py-3 px-2 font-bold font-mono text-cyan-400">${formatNumber(primaryValue)}</td>
            <td class="py-3 px-2">${otherMetrics}</td>
          `;
          tableBody.appendChild(row);
        });
      }
    } else {
      if (table) table.classList.add("hidden");
      if (placeholder) placeholder.style.display = "block";
    }
  }
  
  renderMetricsChart(evaluation);
}

function renderMetricsChart(evaluation) {
  const canvas = document.getElementById("metrics-chart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  
  const evaluations = evaluation?.evaluations || [];
  if (!evaluations.length) {
    if (state.chart) {
      state.chart.destroy();
      state.chart = null;
    }
    canvas.style.display = "none";
    let placeholder = document.getElementById("metrics-chart-placeholder");
    if (!placeholder) {
      placeholder = document.createElement("div");
      placeholder.id = "metrics-chart-placeholder";
      placeholder.className = "text-xs text-slate-500 font-mono text-center py-20 bg-slate-950/20 rounded-md border border-dashed border-white/5";
      placeholder.textContent = "Awaiting model evaluation data to render comparison chart.";
      canvas.parentNode.appendChild(placeholder);
    } else {
      placeholder.style.display = "block";
    }
    return;
  }
  
  canvas.style.display = "block";
  const placeholder = document.getElementById("metrics-chart-placeholder");
  if (placeholder) placeholder.style.display = "none";

  const labels = evaluations.map((item) => item.name);
  const values = evaluations.map((item) => choosePrimaryMetric(item.metrics, evaluation?.primary_metric));
  
  const primaryMetric = evaluation?.primary_metric || "score";
  const barGradient = getChartGradient(ctx, "rgba(34, 197, 94, 0.85)", "rgba(6, 182, 212, 0.15)");
  const borderGradient = getChartGradient(ctx, "rgba(34, 197, 94, 1)", "rgba(6, 182, 212, 0.7)");

  const data = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: barGradient,
        borderColor: borderGradient,
        borderWidth: 1.5,
        borderRadius: 5,
        hoverBackgroundColor: getChartGradient(ctx, "rgba(34, 197, 94, 1)", "rgba(6, 182, 212, 0.35)"),
        hoverBorderColor: "#ffffff",
      },
    ],
  };

  const config = {
    type: "bar",
    data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { 
            color: "#94a3b8",
            font: { family: "'Fira Code', monospace", size: 10 }
          },
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          border: { dash: [5, 5] }
        },
        x: {
          ticks: { 
            color: "#94a3b8",
            font: { family: "'Space Grotesk', sans-serif", size: 11 }
          },
          grid: { display: false },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(9, 9, 11, 0.95)",
          titleColor: "#ffffff",
          bodyColor: "#22c55e",
          borderColor: "rgba(255, 255, 255, 0.08)",
          borderWidth: 1,
          padding: 10,
          titleFont: { family: "'Space Grotesk', sans-serif", size: 12 },
          bodyFont: { family: "'Fira Code', monospace", size: 11 },
          cornerRadius: 6,
          displayColors: false,
          callbacks: {
            label: function(context) {
              return ` ${primaryMetric.toUpperCase()}: ${context.parsed.y.toFixed(4)}`;
            }
          }
        },
      },
    },
  };
  
  if (state.chart) {
    state.chart.destroy();
  }
  state.chart = new Chart(canvas, config);
}

function choosePrimaryMetric(metrics, primaryMetric) {
  if (!metrics) return 0;
  if (primaryMetric && typeof metrics[primaryMetric] !== "undefined") {
    return metrics[primaryMetric];
  }
  const firstValue = Object.values(metrics).find((value) => typeof value === "number");
  return typeof firstValue === "number" ? firstValue : 0;
}

function formatNumber(value) {
  if (typeof value === "number") {
    return Number.isInteger(value) ? value : value.toFixed(4);
  }
  return String(value);
}

async function initPredictionPage() {
  const predictButton = document.getElementById("predict-button");
  const helpButton = document.getElementById("prediction-help-button");
  const clearButton = document.getElementById("prediction-clear-button");
  const sampleButton = document.getElementById("prediction-sample-button");
  
  predictButton?.addEventListener("click", async () => {
    await runPrediction().catch((error) => showToast(error.message, true));
  });
  
  helpButton?.addEventListener("click", () => {
    showToast("Input must be a JSON array of row objects matching training columns.", false);
  });
  
  clearButton?.addEventListener("click", () => {
    const inputArea = document.getElementById("prediction-input");
    if (inputArea) inputArea.value = "";
    showToast("Prediction studio workspace cleared.", false);
  });
  
  sampleButton?.addEventListener("click", () => {
    const inputEl = document.getElementById("prediction-input");
    if (!inputEl) return;
    
    const task = state.session?.task;
    if (task && task.feature_columns && task.feature_columns.length > 0) {
      const sampleRow = {};
      task.feature_columns.forEach(col => {
        let val = 1.0;
        if (task.profile && task.profile.dtypes && task.profile.dtypes[col]) {
          const dtype = String(task.profile.dtypes[col]).toLowerCase();
          if (dtype.includes("int") || dtype.includes("float")) {
            val = 25.0;
          } else if (dtype.includes("bool")) {
            val = true;
          } else {
            val = "value";
          }
        }
        sampleRow[col] = val;
      });
      
      inputEl.value = JSON.stringify([sampleRow, sampleRow], null, 2);
      showToast("Trained dataset features sample loaded.", false);
    } else {
      inputEl.value = '[\n  {\n    "age": 28,\n    "income": 55000\n  },\n  {\n    "age": 42,\n    "income": 72000\n  }\n]';
      showToast("Default sample JSON loaded.", false);
    }
  });
  
  renderPredictionControls();
}

function renderPredictionControls() {
  const modelSelect = document.getElementById("prediction-model");
  const modelInfo = document.getElementById("prediction-model-info");
  if (!modelSelect) return;
  modelSelect.innerHTML = "";
  
  const models = state.session?.trained_models || [];
  if (!models.length) {
    modelSelect.innerHTML = `<option value="">No trained models available</option>`;
    if (modelInfo) {
      modelInfo.textContent = "Train models first to enable predictions.";
    }
    return;
  }
  
  models.forEach((model) => {
    const option = document.createElement("option");
    option.value = model;
    option.textContent = model;
    if (state.session?.best_model && model === state.session.best_model) {
      option.selected = true;
    }
    modelSelect.appendChild(option);
  });
  
  if (modelInfo) {
    modelInfo.textContent = state.session?.best_model
      ? `Recommended Best model: ${state.session.best_model}`
      : `${models.length} model(s) ready for prediction.`;
  }
}

async function runPrediction() {
  const modelSelect = document.getElementById("prediction-model");
  const inputValue = document.getElementById("prediction-input").value.trim();
  const modelName = modelSelect?.value;
  
  if (!modelName) {
    throw new Error("Please select a trained model first.");
  }
  if (!inputValue) {
    throw new Error("Prediction input cannot be empty.");
  }
  
  let rows;
  try {
    rows = JSON.parse(inputValue);
  } catch {
    throw new Error("Prediction payload is invalid JSON. Ensure format matches the guide.");
  }
  
  if (!Array.isArray(rows)) {
    rows = [rows];
  }
  
  const loader = document.getElementById("loading-overlay");
  if (loader) loader.classList.remove("hidden");

  try {
    const payload = await apiFetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_name: modelName, rows }),
    });
    renderPredictionResult(payload);
    showToast("Predictions computed successfully.", false);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (loader) loader.classList.add("hidden");
  }
}

function renderPredictionResult(payload) {
  const resultContainer = document.getElementById("prediction-result");
  const emptyState = document.getElementById("prediction-empty-state");
  if (!resultContainer) return;
  
  if (emptyState) emptyState.style.display = "none";
  resultContainer.classList.remove("hidden");
  
  const predictions = payload.predictions || [];
  
  if (!predictions.length) {
    resultContainer.innerHTML = `<div class="text-slate-500 font-mono text-center py-4">No prediction records returned.</div>`;
    return;
  }
  
  let html = `
    <div class="border-b border-white/5 pb-2 mb-3">
      <span class="text-[10px] text-slate-500 block uppercase font-mono">Model Engine</span>
      <span class="text-xs text-cyan-400 font-bold font-mono">${payload.model_name}</span>
      <span class="text-slate-400 font-mono text-[10px] ml-2">(${predictions.length} records processed)</span>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-left text-xs font-mono border-collapse">
        <thead>
          <tr class="border-b border-white/10 text-slate-400">
            <th class="py-2 px-1 text-slate-400">#</th>
            <th class="py-2 px-1 text-slate-200 font-bold">Prediction Output</th>
            <th class="py-2 px-1 text-slate-400">Probabilities / Details</th>
          </tr>
        </thead>
        <tbody>
  `;
  
  predictions.forEach((record, index) => {
    let probText = "-";
    if (record.probabilities) {
      if (Array.isArray(record.probabilities)) {
        probText = record.probabilities.map((p, idx) => `[${idx}]: ${(p * 100).toFixed(1)}%`).join(", ");
      } else if (typeof record.probabilities === "object") {
        probText = Object.entries(record.probabilities)
          .map(([k, v]) => `<span class="inline-block bg-slate-950 border border-white/5 rounded px-2 py-0.5 mr-1 mb-1 text-[10px] text-slate-400">${k}: ${(v * 100).toFixed(1)}%</span>`)
          .join("");
      }
    }
    
    let predBadge = `<span class="text-slate-200 font-semibold">${record.prediction}</span>`;
    if (typeof record.prediction === "number") {
      predBadge = `<span class="text-violet-400 font-bold font-mono">${record.prediction}</span>`;
    } else if (typeof record.prediction === "string") {
      predBadge = `<span class="text-emerald-400 font-bold">${record.prediction}</span>`;
    }
    
    html += `
      <tr class="border-b border-white/[0.02] last:border-0 hover:bg-white/[0.01]">
        <td class="py-2.5 px-1 text-slate-600">${index + 1}</td>
        <td class="py-2.5 px-1">${predBadge}</td>
        <td class="py-2.5 px-1">${probText}</td>
      </tr>
    `;
  });
  
  html += `
        </tbody>
      </table>
    </div>
  `;
  
  resultContainer.innerHTML = html;
}

async function generateReport() {
  const title = document.getElementById("report-title")?.value.trim() || "AutoDS-LLM Model Sweep Summary";
  
  const loader = document.getElementById("loading-overlay");
  if (loader) loader.classList.remove("hidden");

  try {
    const payload = await apiFetch("/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    
    const status = document.getElementById("report-status");
    if (status) {
      status.classList.remove("hidden");
      status.innerHTML = `
        <div class="flex items-center gap-2 mb-2">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <strong class="text-slate-200">Executive AutoML Report Successfully Built</strong>
        </div>
        <div class="space-y-1 text-slate-400">
          <p>📄 <span class="font-semibold text-slate-300">JSON path:</span> <span class="text-cyan-500 font-bold">${payload.json_path}</span></p>
          <p>📝 <span class="font-semibold text-slate-300">Markdown path:</span> <span class="text-cyan-500 font-bold">${payload.markdown_path}</span></p>
        </div>
      `;
    }
    showToast("AutoML report generated successfully.", false);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (loader) loader.classList.add("hidden");
  }
}

async function apiFetch(path, options = {}) {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const response = await fetch(url, options);
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!response.ok) {
    const message = data?.detail || data?.message || data || `Request failed with status ${response.status}`;
    throw new Error(message);
  }
  return data;
}

async function fetchText(path) {
  const response = await fetch(path);
  return await response.text();
}

function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.className = "toast-notification show";
  if (isError) {
    toast.classList.add("error");
  } else {
    toast.classList.add("success");
  }
  
  gsap.fromTo(toast, { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" });
  
  clearTimeout(toast.dismissTimer);
  toast.dismissTimer = setTimeout(() => {
    gsap.to(toast, { y: 20, opacity: 0, duration: 0.3, ease: "power2.in", onComplete: () => {
      toast.classList.remove("show");
    } });
  }, 4000);
}

function getChartGradient(ctx, colorStart, colorEnd) {
  const chartArea = ctx.chartArea;
  if (!chartArea) return colorStart; // Fallback if chart isn't fully rendered yet

  const gradient = ctx.ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
  gradient.addColorStop(0, colorStart);
  gradient.addColorStop(1, colorEnd);
  return gradient;
}

function animateMetricCards() {
  const cards = document.querySelectorAll(".glass-card");
  gsap.fromTo(
    cards,
    { opacity: 0, y: 15 },
    { opacity: 1, y: 0, duration: 0.45, stagger: 0.06, ease: "power2.out" }
  );
}