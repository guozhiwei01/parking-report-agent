from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict


class ReportState(TypedDict, total=False):
    job_id: str
    template_path: str
    data_path: str
    output_path: str
    instructions: Optional[str]
    metrics: Dict[str, Any]
    profile: Dict[str, Any]
    plan: Dict[str, Any]
    narrative: Dict[str, Any]
    charts: List[str]
