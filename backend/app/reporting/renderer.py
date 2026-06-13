from pathlib import Path
from typing import Any, Dict, List

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Inches


def render_report_docx(
    template_path: str,
    output_path: Path,
    metrics: Dict[str, Any],
    profile: Dict[str, Any],
    report_draft: Dict[str, Any],
    chart_paths: List[str],
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = Document(template_path)
    document._body.clear_content()

    document.add_heading("停车明细分析报告", level=1)
    document.add_paragraph(report_draft["executive_summary"])

    document.add_heading("一、核心指标", level=2)
    table = document.add_table(rows=1, cols=2)
    try:
        table.style = "Table Grid"
    except KeyError:
        pass
    table.rows[0].cells[0].text = "指标"
    table.rows[0].cells[1].text = "结果"
    rows = [
        ("总交易笔数", f"{metrics['total_transactions']} 笔"),
        ("应收总金额", f"{metrics['receivable_amount']:.2f} 元"),
        ("实收总金额", f"{metrics['collected_amount']:.2f} 元"),
        ("实际抵扣总额", f"{metrics['actual_deduct_amount']:.2f} 元"),
        ("实收率", f"{metrics['collection_rate']:.1f}%"),
        ("主要支付方式", f"{metrics['top_payment_method']}（{metrics['top_payment_method_count']} 笔）"),
    ]
    for name, value in rows:
        cells = table.add_row().cells
        cells[0].text = name
        cells[1].text = value

    document.add_heading("二、交易画像", level=2)
    document.add_paragraph(
        f"平均停车时长 {profile['duration']['average_hours']} 小时，"
        f"最长停车时长 {profile['duration']['max_hours']} 小时。"
    )
    for chart_path in chart_paths:
        document.add_picture(chart_path, width=Inches(6.2))

    document.add_heading("三、补充观察", level=2)
    for observation in report_draft["observations"]:
        add_paragraph_with_optional_style(document, observation, "List Bullet", "· ")

    document.add_heading("四、管理建议", level=2)
    for index, recommendation in enumerate(report_draft["recommendations"], start=1):
        add_paragraph_with_optional_style(document, recommendation, "List Number", f"{index}. ")

    document.save(output_path)
    return output_path


def add_paragraph_with_optional_style(document: Document, text: str, style: str, fallback_prefix: str) -> None:
    if has_paragraph_style(document, style):
        document.add_paragraph(text, style=style)
    else:
        document.add_paragraph(f"{fallback_prefix}{text}")


def has_paragraph_style(document: Document, style: str) -> bool:
    return any(item.name == style and item.type == WD_STYLE_TYPE.PARAGRAPH for item in document.styles)
