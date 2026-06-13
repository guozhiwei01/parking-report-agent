# Agent 工作流

实现方式是：单智能体 + LangGraph 状态工作流。

推荐图结构：

```text
load_inputs
  -> compute_hard_metrics
  -> profile_transactions
  -> plan_report_with_llm
  -> draft_narrative_with_llm
  -> generate_charts
  -> render_docx
  -> persist_success
```

任意节点失败时，要把任务更新为 failed，并记录有用的错误信息。

规则：

- 确定性节点只负责计算事实和候选信号。
- LLM 节点负责选择重点、组织表达、生成报告文字。
- LLM 不能计算或覆盖六个硬指标。
- Graph state 要能序列化、能调试。
- Agent loop 必须有边界，最多做有限次校验/修订，不做无限自主循环。
- 默认保持单智能体，不引入多智能体角色，除非出现明确需求。
