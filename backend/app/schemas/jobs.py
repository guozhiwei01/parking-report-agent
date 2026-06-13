from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import ReportJob


class JobResponse(BaseModel):
    id: str
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str]

    @classmethod
    def from_job(cls, job: ReportJob) -> "JobResponse":
        return cls(
            id=job.id,
            status=job.status,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
            download_url=f"/api/jobs/{job.id}/download" if job.status == "completed" else None,
        )
