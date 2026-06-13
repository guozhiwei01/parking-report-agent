# API 契约

后端提供 JSON API，前端只依赖这些接口。

核心接口：

```text
POST /api/jobs
GET /api/jobs/{job_id}
GET /api/jobs/{job_id}/download
```

`POST /api/jobs` 使用 multipart form data：

- `template_file`：DOCX 模板。
- `data_file`：CSV 数据。
- `instructions`：可选文本，用于调试或引导 Agent。

任务状态只使用这些值：

- `queued`
- `running`
- `completed`
- `failed`

提交接口必须快速返回 job id，不能等待报告生成完成。

状态接口至少返回：

- job id
- status
- error message，如果失败
- created_at
- updated_at
- download_url，如果完成

下载接口只允许 completed job 下载。未完成任务应返回合适的 4xx 错误。

API 层不要直接执行业务生成逻辑，要通过 job service 和 generation harness。
