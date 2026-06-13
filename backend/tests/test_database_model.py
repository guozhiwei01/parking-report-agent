from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import JOB_STATUSES, ReportJob


def test_report_job_defaults() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        job = ReportJob(template_path="storage/uploads/job/template.docx", data_path="storage/uploads/job/data.csv")
        session.add(job)
        session.commit()
        session.refresh(job)

    assert job.id
    assert len(job.id) == 36
    assert job.status == "queued"
    assert job.status in JOB_STATUSES
    assert job.created_at is not None
    assert job.updated_at is not None
