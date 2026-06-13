from app.reporting.analyzer import analyze_transactions
from app.reporting.llm import ReportDraft, generate_report_draft


def test_stub_report_draft_uses_metrics_without_overriding(monkeypatch) -> None:
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    analysis = analyze_transactions("Interview_materials/data.csv")

    draft = generate_report_draft(
        job_id="job-1",
        metrics=analysis["metrics"],
        profile=analysis["profile"],
    )

    assert isinstance(draft, ReportDraft)
    assert "3674" in draft.executive_summary
    assert "54.3" in draft.executive_summary
    assert "total_transactions" not in draft.model_dump()
