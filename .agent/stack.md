# 技术栈

除非用户明确改变方向，否则使用以下技术栈：

- FastAPI：HTTP API。
- 原生 HTML / JavaScript / CSS：极简上传、状态查询、下载前端。
- PostgreSQL：持久化任务状态。
- SQLAlchemy / Alembic：数据库访问和迁移。
- LangGraph：报表生成 Agent 的工作流运行时。
- LangChain：Prompt、结构化模型调用和模型抽象。
- LangSmith：配置了凭证时用于 tracing。
- Qwen OpenAI-compatible API：LLM 调用。
- pandas：确定性 CSV 分析。
- matplotlib：生成图表 PNG。
- python-docx：生成 DOCX 报告。
- pytest / httpx：测试。
- Docker Compose：一键启动。

不要默认加入 React、Next.js、Celery、Redis、pgvector/RAG 或多智能体基础设施。

本机虽然有 pgvector，但当前作业不需要语义检索。只有后续要检索历史报告、领域规则或管理者反馈时，才考虑使用。
