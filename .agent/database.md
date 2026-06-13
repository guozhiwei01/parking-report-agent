# 数据库策略

PostgreSQL 只负责持久化任务生命周期和必要元数据，不存大文件内容。

推荐核心表：`report_jobs`

字段至少包括：

- `id`：UUID 主键。
- `status`：queued / running / completed / failed。
- `template_path`：上传 DOCX 路径。
- `data_path`：上传 CSV 路径。
- `output_path`：生成 DOCX 路径，可为空。
- `instructions`：可选处理说明。
- `error_message`：失败原因，可为空。
- `created_at`
- `started_at`
- `completed_at`
- `updated_at`

文件放在本地 `storage/` 下，按 job id 分目录，方便幂等和排查：

```text
storage/uploads/{job_id}/
storage/charts/{job_id}/
storage/reports/{job_id}.docx
```

使用 Alembic 管理 schema 变更。

不要把 LLM 大段 prompt/response 强制入库；题目要求的 LLM 可观测性优先用 JSON logs 和 LangSmith。只有确实需要页面展示或查询时，再加 trace 表。
