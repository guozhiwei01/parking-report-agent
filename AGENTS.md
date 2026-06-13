# Agent 开发指令

这是一个停车报表生成 Agent 的面试项目。

修改代码前，先按任务类型阅读 `.agent/` 目录下的对应文件：

- `.agent/project.md`：项目目标和评分重点。
- `.agent/stack.md`：固定技术栈。
- `.agent/frontend.md`：原生 HTML/JS 前端边界和交互要求。
- `.agent/api.md`：前后端 API 契约和任务状态。
- `.agent/database.md`：数据库模型和迁移约束。
- `.agent/workflow.md`：LangGraph 和 Agent 工作流约束。
- `.agent/harness.md`：生成 Harness 的职责边界。
- `.agent/report-requirements.md`：报表、硬指标和 DOCX 输出要求。
- `.agent/observability.md`：结构化日志、LangSmith 和可观测性要求。
- `.agent/sdd-tdd.md`：轻量 SDD/TDD 约束。
- `.agent/delivery.md`：Docker、README 和样例报告交付要求。
- `.agent/git.md`：提交纪律。
- `.agent/secrets.md`：环境变量和密钥处理。

最高优先级规则：

- 不要提交真实 API key、数据库密码、`.env` 或包含敏感信息的日志。
- 报表硬指标必须由代码确定性计算，不能交给 LLM。
- Agent 栈使用 LangGraph / LangChain，LangSmith 可配置启用，不要改成自研 LLM runner。
- 前端使用原生 HTML、简单 JavaScript 和原生 CSS，不要引入 Vue/React。
- 项目范围控制在 6 小时面试作业能完成的复杂度。
- 每完成一个完整原子功能就提交，不要堆成一个巨大的最终提交。
