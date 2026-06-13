from pathlib import Path

from app.core.config import get_settings
from app.workflow.graph import build_report_graph


def test_report_graph_runs_with_fake_nodes(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    get_settings.cache_clear()

    final_state = build_report_graph().invoke(
        {
            "job_id": "job-1",
            "template_path": "template.docx",
            "data_path": "data.csv",
            "instructions": None,
        }
    )

    assert final_state["output_path"].endswith("job-1.docx")
    assert Path(final_state["output_path"]).exists()
    get_settings.cache_clear()
