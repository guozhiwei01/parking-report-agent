from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import ReportJob


def create_job(db: Session, instructions: Optional[str] = None) -> ReportJob:
    job = ReportJob(
        status="queued",
        template_path="pending",
        data_path="pending",
        instructions=instructions,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> Optional[ReportJob]:
    return db.get(ReportJob, job_id)


async def save_upload_file(job_id: str, filename: str, upload_file: UploadFile) -> Path:
    upload_dir = Path(get_settings().storage_dir) / "uploads" / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = upload_dir / filename
    with target_path.open("wb") as output:
        while chunk := await upload_file.read(1024 * 1024):
            output.write(chunk)
    return target_path
