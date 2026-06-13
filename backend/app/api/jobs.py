from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.jobs import JobResponse
from app.services.generation import run_generation_harness
from app.services.jobs import create_job, get_job, save_upload_file
from app.services.logging import log_event

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=202)
async def submit_job(
    background_tasks: BackgroundTasks,
    template_file: UploadFile = File(...),
    data_file: UploadFile = File(...),
    instructions: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
) -> JobResponse:
    if not template_file.filename or not template_file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="template_file must be a .docx file")
    if not data_file.filename or not data_file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="data_file must be a .csv file")

    job = create_job(db=db, instructions=instructions)
    template_path = await save_upload_file(job.id, "template.docx", template_file)
    data_path = await save_upload_file(job.id, "data.csv", data_file)
    job.template_path = str(template_path)
    job.data_path = str(data_path)
    db.commit()
    db.refresh(job)

    log_event("job.created", job_id=job.id, status=job.status)
    background_tasks.add_task(run_generation_harness, job.id)
    return JobResponse.from_job(job)


@router.get("/{job_id}", response_model=JobResponse)
def read_job(job_id: str, db: Session = Depends(get_db)) -> JobResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return JobResponse.from_job(job)


@router.get("/{job_id}/download")
def download_job(job_id: str, db: Session = Depends(get_db)) -> FileResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != "completed" or not job.output_path:
        raise HTTPException(status_code=409, detail="job is not completed")

    log_event("job.download", job_id=job.id, status=job.status)
    return FileResponse(
        path=job.output_path,
        filename=f"parking-report-{job.id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
