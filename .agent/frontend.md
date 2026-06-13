# 前端策略

前端使用 Vue3，不使用服务端模板。

推荐技术栈：

- Vue3
- Vite
- TypeScript
- 原生 CSS

页面范围控制在一个最小可用应用：

- 上传模板 DOCX。
- 上传交易 CSV。
- 输入可选处理说明。
- 提交后显示 job id 和任务状态。
- 页面刷新后可以通过 job id 恢复状态。
- running / queued 状态下可以轮询。
- completed 状态下显示下载按钮。
- failed 状态下显示错误信息。

前端通过 FastAPI JSON API 交互。接口细节以 `.agent/api.md` 为准：

```text
POST /api/jobs
GET /api/jobs/{job_id}
GET /api/jobs/{job_id}/download
```

规则：

- 不引入复杂 UI 组件库，除非用户明确要求。
- 不引入 Pinia，除非状态复杂到确实需要。
- 不做认证、权限、历史任务列表或在线 DOCX 预览。
- 保持界面朴素、清楚、可用，时间优先留给 Agent 和报表生成。
- Docker Compose 中前端可以独立构建，也可以由后端服务静态托管构建产物。
