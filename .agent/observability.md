# 可观测性

每个用户请求和任务生命周期变化都要输出结构化 JSON 日志。

重要 job 事件包括：

- 收到上传
- 创建任务
- 任务开始
- graph 节点开始 / 完成 / 失败
- 报告生成完成
- 任务完成
- 任务失败
- 下载请求

每次 LLM 调用都要记录：

- job id
- graph 节点名
- model
- prompt 或 message payload
- 结构化响应
- latency
- error，如果有

配置了 `LANGCHAIN_API_KEY` 和 tracing 相关环境变量时，启用 LangSmith tracing。

本地 JSON 日志仍然必须保留，因为题目明确要求可检查的结构化输出。

不要记录 API key、数据库密码或完整 `.env` 内容。
