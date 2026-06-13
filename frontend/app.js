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

let pollTimer;

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
  jobStatusText.textContent = job.status;

  jobError.hidden = !job.error_message;
  jobError.textContent = job.error_message || "";

  downloadLink.hidden = !job.download_url;
  if (job.download_url) {
    downloadLink.href = job.download_url;
  }
}

function renderError(error) {
  statusPanel.hidden = false;
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
