from pathlib import Path
from typing import Any, Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager


def configure_chart_fonts() -> None:
    candidates = [
        "Noto Sans CJK SC",
        "Noto Sans CJK JP",
        "Noto Serif CJK SC",
        "PingFang SC",
        "Heiti SC",
        "Arial Unicode MS",
        "SimHei",
    ]
    available = {font.name for font in font_manager.fontManager.ttflist}
    for font_name in candidates:
        if font_name in available:
            plt.rcParams["font.sans-serif"] = [font_name]
            break
    plt.rcParams["axes.unicode_minus"] = False


def generate_report_charts(job_id: str, profile: Dict[str, Any], charts_dir: Path) -> List[str]:
    configure_chart_fonts()
    charts_dir.mkdir(parents=True, exist_ok=True)
    payment_chart = charts_dir / f"{job_id}-payment-methods.png"
    duration_chart = charts_dir / f"{job_id}-duration-bins.png"

    _bar_chart(
        output_path=payment_chart,
        labels=[item["name"] for item in profile["payment_method_counts"]],
        values=[item["count"] for item in profile["payment_method_counts"]],
        title="支付方式分布",
        ylabel="交易笔数",
    )
    _bar_chart(
        output_path=duration_chart,
        labels=[item["range"] for item in profile["duration"]["bins"]],
        values=[item["count"] for item in profile["duration"]["bins"]],
        title="停车时长分布",
        ylabel="交易笔数",
    )
    return [str(payment_chart), str(duration_chart)]


def _bar_chart(output_path: Path, labels: List[str], values: List[int], title: str, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    ax.bar(labels, values, color="#146c5f")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", color="#d8dee4", linewidth=0.7)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
