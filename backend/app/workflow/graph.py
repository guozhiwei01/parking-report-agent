from pathlib import Path
from typing import Callable

from langgraph.graph import END, StateGraph

from app.core.config import get_settings
from app.reporting.analyzer import analyze_transactions
from app.reporting.charts import generate_report_charts
from app.reporting.llm import generate_report_draft
from app.reporting.renderer import render_report_docx
from app.services.logging import log_event
from app.workflow.state import ReportState


Node = Callable[[ReportState], ReportState]


def logged_node(name: str, node: Node) -> Node:
    def wrapper(state: ReportState) -> ReportState:
        job_id = state["job_id"]
        log_event("graph.node.started", job_id=job_id, node=name)
        try:
            next_state = node(state)
        except Exception as exc:
            log_event("graph.node.failed", job_id=job_id, node=name, error=str(exc))
            raise
        log_event("graph.node.completed", job_id=job_id, node=name)
        return next_state

    return wrapper


def load_inputs(state: ReportState) -> ReportState:
    return state


def compute_hard_metrics(state: ReportState) -> ReportState:
    analysis = analyze_transactions(state["data_path"])
    return {**state, "metrics": analysis["metrics"], "profile": analysis["profile"]}


def profile_transactions(state: ReportState) -> ReportState:
    return state


def decide_profile_branch(state: ReportState) -> str:
    metrics = state["metrics"]
    profile = state["profile"]
    receivable = metrics["receivable_amount"] or 1
    deduct_ratio = metrics["actual_deduct_amount"] / receivable
    has_long_stay = any(
        item["type"] == "long_stay_over_12h" and item["count"] > 0
        for item in profile["anomaly_candidates"]
    )

    if deduct_ratio >= 0.3 or has_long_stay:
        return "enrich_risk_findings"
    return "plan_report_with_llm"


def enrich_risk_findings(state: ReportState) -> ReportState:
    metrics = state["metrics"]
    profile = state["profile"]
    flags = []
    receivable = metrics["receivable_amount"] or 1
    deduct_ratio = metrics["actual_deduct_amount"] / receivable
    if deduct_ratio >= 0.3:
        flags.append("high_deduct_ratio")
    for item in profile["anomaly_candidates"]:
        if item["type"] == "long_stay_over_12h" and item["count"] > 0:
            flags.append("long_stay_records")
    return {**state, "risk_flags": flags}


def plan_report_with_llm(state: ReportState) -> ReportState:
    sections = ["经营概览", "支付结构", "停车时长", "管理建议"]
    if state.get("risk_flags"):
        sections.insert(3, "风险提示")
    return {**state, "plan": {"sections": sections, "risk_flags": state.get("risk_flags", [])}}


def draft_narrative_with_llm(state: ReportState) -> ReportState:
    draft = generate_report_draft(
        job_id=state["job_id"],
        metrics=state["metrics"],
        profile=state["profile"],
        instructions=state.get("instructions") or "",
    )
    return {**state, "report_draft": draft.model_dump()}


def generate_charts(state: ReportState) -> ReportState:
    chart_dir = Path(get_settings().storage_dir) / "charts" / state["job_id"]
    chart_paths = generate_report_charts(state["job_id"], state["profile"], chart_dir)
    return {**state, "charts": chart_paths}


def render_docx(state: ReportState) -> ReportState:
    reports_dir = Path(get_settings().storage_dir) / "reports"
    output_path = reports_dir / f"{state['job_id']}.docx"
    render_report_docx(
        template_path=state["template_path"],
        output_path=output_path,
        metrics=state["metrics"],
        profile=state["profile"],
        report_draft=state["report_draft"],
        chart_paths=state["charts"],
    )
    return {**state, "output_path": str(output_path)}


def persist_success(state: ReportState) -> ReportState:
    return state


def build_report_graph():
    graph = StateGraph(ReportState)
    graph.add_node("load_inputs", logged_node("load_inputs", load_inputs))
    graph.add_node("compute_hard_metrics", logged_node("compute_hard_metrics", compute_hard_metrics))
    graph.add_node("profile_transactions", logged_node("profile_transactions", profile_transactions))
    graph.add_node("enrich_risk_findings", logged_node("enrich_risk_findings", enrich_risk_findings))
    graph.add_node("plan_report_with_llm", logged_node("plan_report_with_llm", plan_report_with_llm))
    graph.add_node("draft_narrative_with_llm", logged_node("draft_narrative_with_llm", draft_narrative_with_llm))
    graph.add_node("generate_charts", logged_node("generate_charts", generate_charts))
    graph.add_node("render_docx", logged_node("render_docx", render_docx))
    graph.add_node("persist_success", logged_node("persist_success", persist_success))

    graph.set_entry_point("load_inputs")
    graph.add_edge("load_inputs", "compute_hard_metrics")
    graph.add_edge("compute_hard_metrics", "profile_transactions")
    graph.add_conditional_edges(
        "profile_transactions",
        decide_profile_branch,
        {
            "enrich_risk_findings": "enrich_risk_findings",
            "plan_report_with_llm": "plan_report_with_llm",
        },
    )
    graph.add_edge("enrich_risk_findings", "plan_report_with_llm")
    graph.add_edge("plan_report_with_llm", "draft_narrative_with_llm")
    graph.add_edge("draft_narrative_with_llm", "generate_charts")
    graph.add_edge("generate_charts", "render_docx")
    graph.add_edge("render_docx", "persist_success")
    graph.add_edge("persist_success", END)
    return graph.compile()
