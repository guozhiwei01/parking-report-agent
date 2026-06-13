# TODO

本文件是当前面试项目的执行清单。每完成一个完整条目并通过验收，就做一次原子提交。

## 1. 项目脚手架和依赖

- [ ] 创建后端 Python 包结构。
- [ ] 添加后端依赖文件。
- [ ] 创建 Vue3 / Vite / TypeScript 前端。
- [ ] 添加 `.env.example`。

验收：

- [ ] 后端依赖可安装。
- [ ] 前端依赖可安装。
- [ ] 不包含真实密钥。

建议提交：`Scaffold backend and frontend`

## 2. 数据库模型和迁移

- [ ] 创建 PostgreSQL 配置读取。
- [ ] 定义 `report_jobs` 模型。
- [ ] 配置 Alembic。
- [ ] 添加初始迁移。

验收：

- [ ] 能创建或迁移数据库表。
- [ ] job 状态字段覆盖 queued / running / completed / failed。

建议提交：`Add job persistence`

## 3. Job API

- [ ] 实现 `POST /api/jobs`。
- [ ] 实现 `GET /api/jobs/{job_id}`。
- [ ] 实现 `GET /api/jobs/{job_id}/download`。
- [ ] 保存上传文件到 job 专属目录。
- [ ] 接入后台任务入口，但生成逻辑可先 mock。

验收：

- [ ] 提交请求快速返回 job id。
- [ ] 状态刷新后仍可查询。
- [ ] 未完成任务不能下载。

建议提交：`Add job API lifecycle`

## 4. Vue3 前端

- [ ] 实现上传表单。
- [ ] 实现可选 instructions 输入框。
- [ ] 实现 job 状态展示。
- [ ] 实现 queued / running 轮询。
- [ ] 实现 completed 下载按钮和 failed 错误展示。

验收：

- [ ] 前端可调用后端 API。
- [ ] 刷新后可通过 job id 恢复状态。
- [ ] 页面保持简单可用。

建议提交：`Add Vue job submission UI`

## 5. LangGraph 工作流骨架

- [ ] 定义 graph state。
- [ ] 实现 generation harness。
- [ ] 创建 LangGraph 节点骨架。
- [ ] 接入 job 状态更新。
- [ ] 添加节点级结构化日志。

验收：

- [ ] graph 可以用 fake 节点跑完整流程。
- [ ] 成功和失败都会更新 job 状态。

建议提交：`Add LangGraph generation workflow`

## 6. 确定性分析器

- [ ] 解析 CSV。
- [ ] 计算六个硬指标。
- [ ] 生成支付方式、渠道、停车时长和异常候选画像。
- [ ] 增加 analyzer 单元测试。

验收：

- [ ] 样例 CSV 六个硬指标计算正确。
- [ ] LLM 不参与硬指标计算。

建议提交：`Add deterministic transaction analysis`

## 7. LLM 报告规划和文字生成

- [ ] 接入 Qwen OpenAI-compatible API。
- [ ] 使用 LangChain prompt 和结构化输出。
- [ ] 支持 LangSmith tracing。
- [ ] 没有 key 时提供 fake/stub LLM。
- [ ] 校验 LLM 输出不能覆盖硬指标。

验收：

- [ ] LLM 调用有 JSON 日志。
- [ ] 输出包含补充观察和建议。
- [ ] 本地无 key 时测试仍可跑。

建议提交：`Add LLM report planning`

## 8. 图表和 DOCX 渲染

- [ ] 生成至少一张真实图表 PNG。
- [ ] 使用 python-docx 生成最终报告。
- [ ] 填入六个硬指标。
- [ ] 插入 Agent 生成的观察和建议。
- [ ] 输出到 `storage/reports/{job_id}.docx`。

验收：

- [ ] 生成文件是可打开的 `.docx`。
- [ ] 报告包含至少一张真实图表。
- [ ] 硬指标值与 analyzer 一致。

建议提交：`Render DOCX parking report`

## 9. API 级测试

- [ ] 编写 submit -> status -> download 测试。
- [ ] mock generation harness。
- [ ] 覆盖失败或未完成下载路径。

验收：

- [ ] `pytest` 通过。
- [ ] 测试不依赖真实 LLM。

建议提交：`Add API lifecycle tests`

## 10. Docker Compose

- [ ] 添加后端 Dockerfile。
- [ ] 添加前端 Dockerfile 或构建流程。
- [ ] 添加 `docker-compose.yml`。
- [ ] 配置 Postgres 服务。

验收：

- [ ] `docker compose up --build` 可以启动系统。
- [ ] README 中说明本机 Docker CLI 路径问题。

建议提交：`Add Docker Compose setup`

## 11. README 和样例报告

- [ ] 编写 README。
- [ ] 说明运行方式、测试方式和环境变量。
- [ ] 说明 LangGraph / LangChain / LangSmith 设计。
- [ ] 说明确定性计算和 LLM 推理边界。
- [ ] 用提供材料生成样例报告并放入 `sample_output/`。

验收：

- [ ] 新用户能按 README 跑起来。
- [ ] 样例报告来自真实生成流程。

建议提交：`Document setup and add sample report`
