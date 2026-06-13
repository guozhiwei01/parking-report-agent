from datetime import datetime, timezone

from app.db.models import ReportJob
from app.db.session import SessionLocal
from app.services.logging import log_event
from app.workflow.graph import build_report_graph
from app.workflow.state import ReportState


class GenerationHarness:
    def __init__(self) -> None:
        self.graph = build_report_graph()

    def run(self, job_id: str) -> None:
        with SessionLocal() as db:
            job = db.get(ReportJob, job_id)
            if job is None:
                log_event("job.missing", job_id=job_id)
                return

            try:
                job.status = "running"
                job.started_at = datetime.now(timezone.utc)
                db.commit()
                log_event("job.running", job_id=job.id)

                final_state = self.graph.invoke(self._initial_state(job))
                job.output_path = final_state["output_path"]
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

    def _initial_state(self, job: ReportJob) -> ReportState:
        return {
            "job_id": job.id,
            "template_path": job.template_path,
            "data_path": job.data_path,
            "instructions": job.instructions,
        }
