import os
import time
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import get_settings
from app.services.logging import log_event


class ReportDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executive_summary: str = Field(description="面向管理者的一段总结")
    observations: List[str] = Field(description="有数据支撑的补充观察")
    recommendations: List[str] = Field(description="可执行管理建议")


def generate_report_draft(
    job_id: str,
    metrics: Dict[str, Any],
    profile: Dict[str, Any],
    instructions: str = "",
) -> ReportDraft:
    settings = get_settings()
    prompt = build_prompt(metrics=metrics, profile=profile, instructions=instructions)
    started = time.perf_counter()
    model_name = settings.qwen_model if settings.qwen_api_key else "stub"

    try:
        if settings.qwen_api_key:
            configure_langsmith()
            model = ChatOpenAI(
                api_key=settings.qwen_api_key,
                base_url=settings.qwen_base_url,
                model=settings.qwen_model,
                temperature=0.2,
            )
            draft = model.with_structured_output(ReportDraft).invoke(prompt)
        else:
            draft = stub_report_draft(metrics, profile)

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        log_event(
            "llm.call.completed",
            job_id=job_id,
            node="draft_narrative_with_llm",
            model=model_name,
            prompt=prompt,
            response=draft.model_dump(),
            latency_ms=latency_ms,
        )
        return draft
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        log_event(
            "llm.call.failed",
            job_id=job_id,
            node="draft_narrative_with_llm",
            model=model_name,
            prompt=prompt,
            latency_ms=latency_ms,
            error=str(exc),
        )
        raise


def build_prompt(metrics: Dict[str, Any], profile: Dict[str, Any], instructions: str = "") -> str:
    return (
        "你是停车场经营分析助手。六个硬指标已经由代码计算完成，不能重新计算、改写或覆盖。\n"
        f"硬指标：{metrics}\n"
        f"交易画像：{profile}\n"
        f"用户补充说明：{instructions or '无'}\n"
        "请输出面向管理者的经营摘要、补充观察和可执行建议。"
    )


def stub_report_draft(metrics: Dict[str, Any], profile: Dict[str, Any]) -> ReportDraft:
    channel = profile["payment_channel_counts"][0]
    top_payment = metrics["top_payment_method"]
    rate = metrics["collection_rate"]
    return ReportDraft(
        executive_summary=(
            f"本期共 {metrics['total_transactions']} 笔交易，实收率 {rate}%，"
            f"主要支付方式为{top_payment}。整体收入结构清晰，但抵扣规模需要持续跟踪。"
        ),
        observations=[
            f"{channel['name']}渠道交易 {channel['count']} 笔，是当前最主要的支付入口。",
            f"实际抵扣总额 {metrics['actual_deduct_amount']} 元，应结合会员和优惠策略复盘抵扣效率。",
            f"最长停车时长 {profile['duration']['max_hours']} 小时，长停车辆需要单独关注。",
        ],
        recommendations=[
            "按支付方式和渠道建立周度监控，优先排查高抵扣低实收组合。",
            "对长时间停车记录设置运营复核清单，减少异常占位和漏收风险。",
            "将优惠券、会员积分的抵扣效果与复购指标绑定，避免只看交易笔数。",
        ],
    )


def configure_langsmith() -> None:
    settings = get_settings()
    if settings.langchain_api_key and settings.langchain_tracing_v2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
