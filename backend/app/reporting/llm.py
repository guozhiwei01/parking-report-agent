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
        "请严格按以下 JSON 对象输出，键名必须完全一致，不要新增、改名或嵌套其它键：\n"
        '{\n'
        '  "executive_summary": "面向管理者的一段经营摘要（字符串）",\n'
        '  "observations": ["补充观察1", "补充观察2", "..."],\n'
        '  "recommendations": ["可执行建议1", "可执行建议2", "..."]\n'
        '}\n'
        "observations 与 recommendations 都是字符串数组，每个元素是一句话，不要用对象。\n"
        "补充观察请聚焦对经营决策最有价值的点，例如：应收与实收之间的缺口及其主要成因"
        "（抵扣 / 免费敞口）、优惠或会员渠道带来的收入流失、长停或异常停车、时段规律。"
        "每条观察都要有具体数字支撑，不要泛泛而谈。"
    )


def stub_report_draft(metrics: Dict[str, Any], profile: Dict[str, Any]) -> ReportDraft:
    top_payment = metrics["top_payment_method"]
    rate = metrics["collection_rate"]
    receivable = metrics["receivable_amount"]
    collected = metrics["collected_amount"]
    deduct = metrics["actual_deduct_amount"]
    gap = round(receivable - collected, 2)
    deduct_share = round(deduct / receivable * 100, 1) if receivable else 0.0

    observations = []
    # 核心洞察：应收与实收的缺口几乎全部由抵扣造成（收入流失主因）
    if gap > 0:
        observations.append(
            f"应收 {receivable:.2f} 元、实收 {collected:.2f} 元，缺口 {gap:.2f} 元；"
            f"其中实际抵扣 {deduct:.2f} 元，占应收 {deduct_share}%，是实收率仅 {rate}% 的主因，"
            "属于可量化的收入让利敞口。"
        )
    # 优惠 / 会员敞口：非主流支付方式中靠抵扣的占比
    methods = profile["payment_method_counts"]
    discount_methods = [m for m in methods if m["name"] in {"会员积分", "优惠券"}]
    if discount_methods:
        detail = "、".join(f"{m['name']} {m['count']} 笔" for m in discount_methods)
        total_discount = sum(m["count"] for m in discount_methods)
        share = round(total_discount / metrics["total_transactions"] * 100, 1)
        observations.append(
            f"优惠类支付（{detail}）合计 {total_discount} 笔，占总交易 {share}%，"
            "免费 / 优惠敞口较大，需评估其对实收的拉低作用。"
        )
    # 长停异常
    long_stay = next(
        (item["count"] for item in profile["anomaly_candidates"] if item["type"] == "long_stay_over_12h"),
        0,
    )
    observations.append(
        f"停车超过 12 小时的记录 {long_stay} 笔，最长 {profile['duration']['max_hours']} 小时，"
        "存在长期占位或异常滞留，建议单独核查。"
    )

    return ReportDraft(
        executive_summary=(
            f"本期共 {metrics['total_transactions']} 笔交易，应收 {receivable:.2f} 元、"
            f"实收 {collected:.2f} 元，实收率 {rate}%，主要支付方式为{top_payment}。"
            f"实收率偏低主要源于 {deduct:.2f} 元抵扣，抵扣与免费敞口需重点跟踪。"
        ),
        observations=observations,
        recommendations=[
            "针对抵扣金额最大的支付方式（会员积分 / 优惠券）单列台账，按周复盘让利成本与回报。",
            "对停车超过 12 小时的记录设置运营复核清单，减少异常占位和漏收风险。",
            "将优惠券、会员积分的抵扣效果与复购、客流指标绑定，避免只看交易笔数。",
            "建立应收—实收—抵扣的周度对账，把实收率作为核心经营指标持续监控。",
        ],
    )


def configure_langsmith() -> None:
    settings = get_settings()
    if settings.langchain_api_key and settings.langchain_tracing_v2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
