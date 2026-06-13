from pathlib import Path
from zipfile import ZipFile

from docx import Document

from app.reporting.analyzer import analyze_transactions
from app.reporting.charts import generate_report_charts
from app.reporting.llm import stub_report_draft
from app.reporting.renderer import render_report_docx


def test_render_report_docx_with_chart(tmp_path) -> None:
    template_path = tmp_path / "template.docx"
    Document().save(template_path)
    analysis = analyze_transactions("Interview_materials/data.csv")
    draft = stub_report_draft(analysis["metrics"], analysis["profile"]).model_dump()
    chart_paths = generate_report_charts("job-1", analysis["profile"], tmp_path / "charts")

    output_path = render_report_docx(
        template_path=str(template_path),
        output_path=tmp_path / "report.docx",
        metrics=analysis["metrics"],
        profile=analysis["profile"],
        report_draft=draft,
        chart_paths=chart_paths,
    )

    assert output_path.exists()
    with ZipFile(output_path) as docx:
        assert any(name.startswith("word/media/") for name in docx.namelist())
