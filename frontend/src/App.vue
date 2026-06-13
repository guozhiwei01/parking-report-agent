<template>
  <main class="page">
    <section class="panel">
      <p class="eyebrow">Parking Report Agent</p>
      <h1>停车明细分析报告生成</h1>
      <form class="form" @submit.prevent="submitJob">
        <label>
          <span>报告模板 DOCX</span>
          <input type="file" accept=".docx" required @change="onTemplateChange" />
        </label>

        <label>
          <span>交易明细 CSV</span>
          <input type="file" accept=".csv" required @change="onDataChange" />
        </label>

        <label>
          <span>补充说明</span>
          <textarea v-model="instructions" rows="4" placeholder="可选"></textarea>
        </label>

        <button type="submit" :disabled="submitting || !templateFile || !dataFile">
          {{ submitting ? "提交中" : "生成报告" }}
        </button>
      </form>

      <section v-if="job" class="status">
        <div>
          <span>任务</span>
          <strong>{{ job.id }}</strong>
        </div>
        <div>
          <span>状态</span>
          <strong>{{ job.status }}</strong>
        </div>
        <p v-if="job.error_message" class="error">{{ job.error_message }}</p>
        <a v-if="job.download_url" class="download" :href="job.download_url">下载 DOCX</a>
      </section>

      <form class="lookup" @submit.prevent="loadJob(lookupJobId)">
        <input v-model="lookupJobId" placeholder="输入 job id 恢复状态" />
        <button type="submit" :disabled="!lookupJobId">查询</button>
      </form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

type JobStatus = "queued" | "running" | "completed" | "failed";

interface JobResponse {
  id: string;
  status: JobStatus;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  download_url: string | null;
}

const templateFile = ref<File | null>(null);
const dataFile = ref<File | null>(null);
const instructions = ref("");
const submitting = ref(false);
const job = ref<JobResponse | null>(null);
const lookupJobId = ref("");
let pollTimer: number | undefined;

function onTemplateChange(event: Event) {
  templateFile.value = (event.target as HTMLInputElement).files?.[0] ?? null;
}

function onDataChange(event: Event) {
  dataFile.value = (event.target as HTMLInputElement).files?.[0] ?? null;
}

async function submitJob() {
  if (!templateFile.value || !dataFile.value) {
    return;
  }

  submitting.value = true;
  const formData = new FormData();
  formData.append("template_file", templateFile.value);
  formData.append("data_file", dataFile.value);
  if (instructions.value.trim()) {
    formData.append("instructions", instructions.value.trim());
  }

  try {
    const response = await fetch("/api/jobs", {
      method: "POST",
      body: formData
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    const createdJob = (await response.json()) as JobResponse;
    job.value = createdJob;
    lookupJobId.value = createdJob.id;
    localStorage.setItem("lastJobId", createdJob.id);
    startPolling();
  } finally {
    submitting.value = false;
  }
}

async function loadJob(jobId: string) {
  if (!jobId) {
    return;
  }
  const response = await fetch(`/api/jobs/${jobId}`);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  const currentJob = (await response.json()) as JobResponse;
  job.value = currentJob;
  localStorage.setItem("lastJobId", currentJob.id);
  if (currentJob.status === "queued" || currentJob.status === "running") {
    startPolling();
  } else {
    stopPolling();
  }
}

function startPolling() {
  stopPolling();
  pollTimer = window.setInterval(() => {
    if (job.value) {
      void loadJob(job.value.id);
    }
  }, 1500);
}

function stopPolling() {
  if (pollTimer) {
    window.clearInterval(pollTimer);
    pollTimer = undefined;
  }
}

onMounted(() => {
  const lastJobId = localStorage.getItem("lastJobId");
  if (lastJobId) {
    lookupJobId.value = lastJobId;
    void loadJob(lastJobId);
  }
});

onBeforeUnmount(stopPolling);
</script>
