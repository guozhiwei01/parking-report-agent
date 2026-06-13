from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import ReportJob
from app.db.session import SessionLocal
from app.services.logging import log_event


def run_generation_harness(job_id: str) -> None:
    with SessionLocal() as db:
        job = db.get(ReportJob, job_id)
        if job is None:
            log_event("job.missing", job_id=job_id)
            return

        try:
            mark_running(db, job)
            output_path = write_placeholder_report(job.id)
            job.output_path = str(output_path)
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            log_event("job.completed", job_id=job.id, output_path=job.output_path)
        except Exception as exc:
            db.rollback()
            job = db.get(ReportJob, job_id)
            if job is not None:
                job.status = "failed"
                job.error_message = str(exc)
                db.commit()
            log_event("job.failed", job_id=job_id, error=str(exc))
            raise


def mark_running(db: Session, job: ReportJob) -> None:
    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    db.commit()
    log_event("job.running", job_id=job.id)


def write_placeholder_report(job_id: str) -> Path:
    reports_dir = Path(get_settings().storage_dir) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{job_id}.docx"
    output_path.write_bytes(b"placeholder report")
    return output_path
