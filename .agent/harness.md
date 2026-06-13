# Generation Harness

LangGraph 外面需要包一层很薄的生成 Harness。

Harness 负责：

- 根据 job 记录构造初始 graph state。
- 调用 LangGraph 工作流。
- 管理上传文件、图表、DOCX 输出等 artifact 路径。
- 更新任务生命周期状态。
- 输出结构化日志。
- 给测试提供一个稳定、可 mock 的边界。

API 层应该调用 Harness，不要直接调用单个 graph 节点。

Harness 要让未来添加 retry 变得容易：job 输入应当幂等，artifact 放在稳定的 job 专属目录里。

不要把 Harness 做成自研 Agent runtime。真正的工作流运行时仍然是 LangGraph。
