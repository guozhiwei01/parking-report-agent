# 停车明细分析报告 Agent

这是一个面试 take-home 项目：上传停车交易 CSV 和 DOCX 模板，后端异步生成带图表的停车明细分析报告。

## 技术栈

- 后端：FastAPI、SQLAlchemy、Alembic、PostgreSQL
- Agent：LangGraph 工作流、LangChain 模型封装、LangSmith 可选 tracing
- 模型：Qwen OpenAI-compatible API，默认模型 `qwen3.6-flash`
- 数据和报表：pandas、matplotlib、python-docx
- 前端：原生 HTML、简单 JavaScript、原生 CSS
- 测试：pytest、httpx
- 交付：Docker Compose

## 关键边界

六个硬指标全部由代码确定性计算，LLM 不参与计算，也不能覆盖这些值：

1. 总交易笔数
2. 应收总金额
3. 实收总金额
4. 实际抵扣总额
5. 实收率
6. 主要支付方式

LLM 只负责基于已计算事实生成管理者摘要、补充观察和建议。没有配置 Qwen key 时，系统会使用 stub LLM，方便本地测试和面试评审。

## Agent Workflow

当前是单智能体 LangGraph 状态工作流：

```text
load_inputs
  -> compute_hard_metrics
  -> profile_transactions
  -> enrich_risk_findings（按数据画像条件进入）
  -> plan_report_with_llm
  -> draft_narrative_with_llm
  -> generate_charts
  -> render_docx
  -> persist_success
```

API 层只调用 generation harness，不直接调用 graph 节点。Harness 负责构造 graph state、更新 job 状态、管理 artifact 路径和结构化日志。

`profile_transactions` 后有真实条件分支：当抵扣占比较高或存在 12 小时以上长停记录时，进入 `enrich_risk_findings` 补充风险标记；否则直接进入报告规划节点。这样 Agent 不是单纯脚本串行执行，而是根据确定性画像选择后续分析路径。

异步任务采用 FastAPI `BackgroundTasks` 执行 generation harness，并用 PostgreSQL 持久化 job 状态。Harness 内置有限重试，默认最多 2 次 graph attempt；每次 attempt、失败和重试调度都会输出 JSON 日志。当前没有引入 Celery/Redis，是为了控制面试项目范围，避免做成分布式任务系统。

## 环境变量

复制 `.env.example` 为 `.env`，再填入本地值：

```bash
cp .env.example .env
```

本地已有 PostgreSQL 时，常用变量：

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me
POSTGRES_DB=parking_report_agent
```

Qwen 和 LangSmith 都是可选：

```text
QWEN_API_KEY=replace-me
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.6-flash
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=parking-report-agent
MIN_JOB_SECONDS=2
```

`MIN_JOB_SECONDS` 只用于演示异步任务状态，避免本地 stub 模式下瞬间完成；接入真实 Qwen API 后，主要耗时来自模型调用，可按需设为 `0`。

不要把真实 `.env`、API key、数据库密码提交到仓库。

## 本地运行

后端：

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
PYTHONPATH=backend .venv/bin/alembic -c backend/alembic.ini upgrade head
PYTHONPATH=backend .venv/bin/uvicorn app.main:app --reload
```

前端是静态 HTML 页面，不需要 Node 构建。开发时可以直接用任意静态服务器打开 `frontend/index.html`，或通过 Docker Compose 访问 Nginx 托管页面。

访问：

- 前端页面：http://localhost:8080
- 后端 health：http://localhost:8000/health

## Docker Compose

标准启动：

```bash
docker compose up --build
```

本机如果 `docker` 不在 PATH，但 Docker Desktop 已安装，可以临时使用：

```bash
PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" docker compose up --build
```

Compose 会启动：

- 前端：http://localhost:8080
- 后端：http://localhost:8000
- PostgreSQL 宿主机端口：`55433`，避免撞本机已有的 `5432`

## 测试

```bash
PYTHONPATH=backend .venv/bin/pytest backend/tests
python3 -m py_compile backend/app/main.py
```

API 级测试覆盖了 submit -> status -> download，并 mock generation harness，不依赖真实 LLM。

## 样例报告

样例报告来自 `Interview_materials/data.csv` 和 `Interview_materials/停车明细分析报告_模板.docx` 的真实生成流程：

```text
sample_output/parking-report-sample.docx
```

样例 CSV 的硬指标为：

- 总交易笔数：3674
- 应收总金额：105795.00 元
- 实收总金额：57397.50 元
- 实际抵扣总额：48285.00 元
- 实收率：54.3%
- 主要支付方式：微信（1435 笔）

报告章节结构对齐官方模板 `停车明细分析报告_模板.docx`：

```text
报告信息（数据周期 + 生成时间）
一、关键指标（硬性数字）
二、支付方式与渠道（含支付方式分布图）
三、停车时长分析（含停车时长分布图、每日入场时间分布图、每日收费时间分布图）
四、补充观察（Agent 生成，聚焦收入流失/优惠敞口/长停异常）
五、结论与建议
```

数据周期、逐时入场/收费分布由 `analyzer` 确定性计算，作为 grounded context 传给报表渲染和 LLM；四张图表全部基于真实数据生成，模板自带的示例占位图会在渲染时移除。

## 日志和可观测性

后端会输出结构化 JSON 日志，覆盖用户请求、job 生命周期、graph 节点开始/完成/失败、LLM 调用和下载请求。配置 LangSmith key 后可以开启 tracing；本地 JSON 日志仍然保留，便于评审直接检查。
