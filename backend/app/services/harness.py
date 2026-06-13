import time
from datetime import datetime, timezone
from typing import Optional

from app.core.config import get_settings
from app.db.models import ReportJob
from app.db.session import SessionLocal
from app.services.logging import log_event
from app.workflow.graph import build_report_graph
from app.workflow.state import ReportState


class GenerationHarness:
    max_attempts = 2

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

                started = time.perf_counter()
                final_state = self._invoke_with_retry(job)
                self._wait_for_minimum_runtime(job.id, started)
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

    def _wait_for_minimum_runtime(self, job_id: str, started: float) -> None:
        min_seconds = get_settings().min_job_seconds
        if min_seconds <= 0:
            return
        elapsed = time.perf_counter() - started
        remaining = min_seconds - elapsed
        if remaining <= 0:
            return
        log_event("job.minimum_runtime.wait", job_id=job_id, remaining_seconds=round(remaining, 2))
        time.sleep(remaining)

    def _initial_state(self, job: ReportJob) -> ReportState:
        return {
            "job_id": job.id,
            "template_path": job.template_path,
            "data_path": job.data_path,
            "instructions": job.instructions,
        }

    def _invoke_with_retry(self, job: ReportJob) -> ReportState:
        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                log_event("job.graph_attempt.started", job_id=job.id, attempt=attempt)
                state = self.graph.invoke({**self._initial_state(job), "retry_attempt": attempt})
                log_event("job.graph_attempt.completed", job_id=job.id, attempt=attempt)
                return state
            except Exception as exc:
                last_error = exc
                log_event("job.graph_attempt.failed", job_id=job.id, attempt=attempt, error=str(exc))
                if attempt >= self.max_attempts:
                    break
                log_event("job.retry_scheduled", job_id=job.id, next_attempt=attempt + 1)
        raise RuntimeError(f"generation failed after {self.max_attempts} attempts: {last_error}")
