# 前端策略

前端使用原生 HTML、简单 JavaScript 和原生 CSS，不使用 Vue、React 或其他前端框架。

推荐技术栈：

- HTML
- JavaScript
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
- 不引入前端构建工具，除非后续功能复杂到确实需要。
- 不做认证、权限、历史任务列表或在线 DOCX 预览。
- 保持界面朴素、清楚、可用，时间优先留给 Agent 和报表生成。
- Docker Compose 中前端使用 Nginx 托管静态文件；也可以由后端服务静态托管。
