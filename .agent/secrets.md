# 密钥和配置

配置通过环境变量读取。

本地预期变量：

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
QWEN_API_KEY
QWEN_BASE_URL
QWEN_MODEL
LANGCHAIN_TRACING_V2
LANGCHAIN_API_KEY
LANGCHAIN_PROJECT
```

可以提交 `.env.example`，但里面只能写变量名和安全占位符。即使本地使用默认数据库密码，也不要把真实密码写进提交。

不要提交：

- `.env`
- 真实 API key
- 真实 LangSmith key
- 数据库密码
- 包含敏感请求内容或凭证的日志

如果 key 被意外贴进聊天或终端输出，不要重复展示，并建议项目结束后轮换。
