# 交付要求

最终仓库需要包含：

- 后端源码。
- Vue3 前端源码。
- 数据库迁移。
- Dockerfile 和 docker-compose.yml。
- README.md。
- `.env.example`。
- 至少一个 API 级测试。
- 使用样例数据生成的 DOCX 报告，放在 `sample_output/`。

Docker Compose 应该能一键启动：

```text
docker compose up --build
```

本机如果 `docker` 不在 PATH，可以使用 Docker Desktop 的 CLI 路径运行，但 README 里仍然写标准 Docker 命令。

README 至少说明：

- 项目目标。
- 如何配置环境变量。
- 如何启动。
- 如何运行测试。
- Agent workflow 设计。
- 确定性计算和 LLM 推理的边界。
- LangSmith 是可选 tracing，不是运行必需。

样例报告必须来自提供的 CSV 和模板，不能手工拼一个假文件。
