from pathlib import Path

from docx import Document

from app.core.config import get_settings
from app.workflow.graph import build_report_graph


def test_report_graph_runs_with_fake_nodes(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    get_settings.cache_clear()
    template_path = tmp_path / "template.docx"
    Document().save(template_path)

    final_state = build_report_graph().invoke(
        {
            "job_id": "job-1",
            "template_path": str(template_path),
            "data_path": "Interview_materials/data.csv",
            "instructions": None,
        }
    )

    assert final_state["output_path"].endswith("job-1.docx")
    assert Path(final_state["output_path"]).exists()
    assert final_state["risk_flags"] == ["high_deduct_ratio", "long_stay_records"]
    assert "风险提示" in final_state["plan"]["sections"]
    get_settings.cache_clear()
