# 可观测性样例（结构化日志 + LangSmith Trace）

本目录是一次**真实生成任务**的可观测性留档，供评审直接检查，无需运行项目。
对应作业要求 §4.2/§4.3：记录每个用户请求的生命周期、以及每次 LLM 调用的
prompt / response / model / latency，均为结构化 JSON。

任务 ID：`5cf9b907-5067-4ad6-8e85-432f7dd46966`（数据来自 `Interview_materials/data.csv` + 官方模板）

## 1. `job-run.jsonl` — 后端结构化 JSON 日志（stdout）

一行一个事件（JSON Lines），按时间排序，覆盖完整生命周期：

```
job.created → job.running → job.graph_attempt.started
  → graph.node.started/completed ×（每个 LangGraph 节点）
  → llm.call.completed（含 model / latency_ms / prompt / response 全文）
  → job.graph_attempt.completed → job.completed → job.download
```

要点：
- **每个 graph 节点**都有 `graph.node.started` / `graph.node.completed`，可还原 Agent 执行路径。
- 本次命中了条件分支 `enrich_risk_findings`（抵扣占比 45.6% ≥ 30% 阈值），
  证明 Agent 按数据画像做了非平凡决策，而非固定串行。
- `llm.call.completed` 事件**完整记录** `model`、`latency_ms`、`prompt`、`response`，
  事后可复盘 LLM 行为；失败时对应 `llm.call.failed` 并带 `error`。
- 日志中不含任何 API key / 密钥。

快速查看：
```bash
cat sample_logs/job-run.jsonl | jq -r '"\(.ts[11:19])  \(.event)"'
# 只看 LLM 调用的 prompt/response/model/latency
cat sample_logs/job-run.jsonl | jq 'select(.event=="llm.call.completed")'
```

## 2. `langsmith-trace.json` — LangSmith 分布式追踪导出

同一次任务在 LangSmith 的完整 run 树（`LANGCHAIN_TRACING_V2=true` 时自动上报），
导出了节点树及 LLM 节点的 inputs/outputs。

要点：
- 根节点 `LangGraph`，下挂各确定性节点（compute_hard_metrics / profile_transactions /
  decide_profile_branch / generate_charts / render_docx …）。
- **整棵树里只有 `draft_narrative_with_llm` 下挂了一个 `ChatOpenAI`（Qwen）LLM 调用**，
  其余全是确定性节点 —— 直观体现“硬指标由代码算、LLM 只负责叙述”的边界。
- LLM 节点带 `model=qwen3.6-flash`、token 数、以及结构化 inputs/outputs。

## 3. `job-run-failed.jsonl` — 失败案例日志（可观测性最有价值的场景）

故意提交一个**缺少必需列**（删掉 `支付方式`）的 CSV，展示出错时日志如何精确定位问题。
事件序列：

```
job.created → job.running
  → job.graph_attempt.started (attempt=1)
    → graph.node.completed (load_inputs)
    → graph.node.failed (compute_hard_metrics)  error: CSV missing required columns: 支付方式
  → job.graph_attempt.failed (attempt=1)
  → job.retry_scheduled (next_attempt=2)          ← Harness 有限重试
  → job.graph_attempt.started (attempt=2) … 同样在 compute_hard_metrics 失败
  → job.failed   error: generation failed after 2 attempts: CSV missing required columns: 支付方式
```

要点：
- **故障被定位到具体节点**（`compute_hard_metrics`）和**具体原因**（缺哪一列），无需翻代码。
- 完整体现 `max_attempts=2` 的**有限重试**：失败 → 重试 → 再失败 → 落 `failed`。
- job 状态被持久化为 `failed` 且写入 `error_message`，前端轮询即可展示。

## 复现方式

```bash
docker compose up --build          # 起服务（需在 .env 配 QWEN_API_KEY 才走真实大模型，否则用 stub）
# 前端 http://localhost:8080 上传 data.csv + 模板，或：
curl -F template_file=@Interview_materials/停车明细分析报告_模板.docx \
     -F data_file=@Interview_materials/data.csv http://localhost:8000/api/jobs
docker compose logs backend | grep '^{'   # 即本目录 job-run.jsonl 的来源
```
