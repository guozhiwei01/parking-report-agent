const form = document.querySelector("#job-form");
const templateFile = document.querySelector("#template-file");
const dataFile = document.querySelector("#data-file");
const instructions = document.querySelector("#instructions");
const submitButton = document.querySelector("#submit-button");
const statusPanel = document.querySelector("#status-panel");
const jobIdText = document.querySelector("#job-id");
const jobStatusText = document.querySelector("#job-status");
const jobError = document.querySelector("#job-error");
const downloadLink = document.querySelector("#download-link");
const lookupForm = document.querySelector("#lookup-form");
const lookupJobId = document.querySelector("#lookup-job-id");
const jobProgress = document.querySelector("#job-progress");
const progressMessage = document.querySelector("#progress-message");
const progressElapsed = document.querySelector("#progress-elapsed");

const STATUS_TEXT = {
  queued: "排队中",
  running: "生成中",
  completed: "已完成",
  failed: "失败",
};
const PROGRESS_MESSAGE = {
  queued: "已提交，排队准备中…",
  running: "AI 正在分析数据并撰写报告，通常需 30–60 秒…",
};

let pollTimer;
let elapsedTimer;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!templateFile.files[0] || !dataFile.files[0]) {
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = "提交中";

  try {
    const body = new FormData();
    body.append("template_file", templateFile.files[0]);
    body.append("data_file", dataFile.files[0]);
    if (instructions.value.trim()) {
      body.append("instructions", instructions.value.trim());
    }

    const response = await fetch("/api/jobs", { method: "POST", body });
    if (!response.ok) {
      throw new Error(await response.text());
    }

    const job = await response.json();
    localStorage.setItem("lastJobId", job.id);
    lookupJobId.value = job.id;
    renderJob(job);
    startPolling(job.id);
  } catch (error) {
    renderError(error);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "生成报告";
  }
});

lookupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (lookupJobId.value.trim()) {
    await loadJob(lookupJobId.value.trim());
  }
});

window.addEventListener("load", async () => {
  const lastJobId = localStorage.getItem("lastJobId");
  if (lastJobId) {
    lookupJobId.value = lastJobId;
    await loadJob(lastJobId);
  }
});

async function loadJob(jobId) {
  const response = await fetch(`/api/jobs/${jobId}`);
  if (!response.ok) {
    throw new Error(await response.text());
  }

  const job = await response.json();
  localStorage.setItem("lastJobId", job.id);
  renderJob(job);

  if (job.status === "queued" || job.status === "running") {
    startPolling(job.id);
  } else {
    stopPolling();
  }
}

function renderJob(job) {
  statusPanel.hidden = false;
  jobIdText.textContent = job.id;
  jobStatusText.textContent = STATUS_TEXT[job.status] || job.status;
  jobStatusText.className = `status-badge ${job.status}`;

  const inProgress = job.status === "queued" || job.status === "running";
  jobProgress.hidden = !inProgress;
  if (inProgress) {
    progressMessage.textContent = PROGRESS_MESSAGE[job.status] || "正在生成报告…";
    startElapsed(job.created_at);
  } else {
    stopElapsed();
  }

  jobError.hidden = !job.error_message;
  jobError.textContent = job.error_message || "";

  downloadLink.hidden = !job.download_url;
  if (job.download_url) {
    downloadLink.href = job.download_url;
  }
}

function startElapsed(createdAt) {
  const start = createdAt ? new Date(createdAt).getTime() : Date.now();
  const tick = () => {
    const seconds = Math.max(0, Math.round((Date.now() - start) / 1000));
    progressElapsed.textContent = `已用时 ${seconds}s`;
  };
  stopElapsed();
  tick();
  elapsedTimer = window.setInterval(tick, 1000);
}

function stopElapsed() {
  if (elapsedTimer) {
    window.clearInterval(elapsedTimer);
    elapsedTimer = undefined;
  }
}

function renderError(error) {
  statusPanel.hidden = false;
  jobProgress.hidden = true;
  stopElapsed();
  jobError.hidden = false;
  jobError.textContent = error instanceof Error ? error.message : String(error);
}

function startPolling(jobId) {
  stopPolling();
  pollTimer = window.setInterval(() => {
    loadJob(jobId).catch(renderError);
  }, 1500);
}

function stopPolling() {
  if (pollTimer) {
    window.clearInterval(pollTimer);
    pollTimer = undefined;
  }
}
