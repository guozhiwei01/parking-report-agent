from pathlib import Path

from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import jobs as jobs_api
from app.core.config import get_settings
from app.db.base import Base
from app.db.models import ReportJob
from app.db.session import get_db
from app.main import app


def test_job_submit_status_download_with_mocked_generation(tmp_path, monkeypatch) -> None:
    client, session_factory = build_test_client(tmp_path, monkeypatch)

    def fake_generation(job_id: str) -> None:
        with session_factory() as db:
            job = db.get(ReportJob, job_id)
            output_path = tmp_path / "reports" / f"{job_id}.docx"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            Document().save(output_path)
            job.status = "completed"
            job.output_path = str(output_path)
            db.commit()

    monkeypatch.setattr(jobs_api, "run_generation_harness", fake_generation)

    response = client.post(
        "/api/jobs",
        files={
            "template_file": (
                "template.docx",
                make_docx_bytes(tmp_path),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            "data_file": ("data.csv", Path("Interview_materials/data.csv").read_bytes(), "text/csv"),
        },
        data={"instructions": "api test"},
    )

    assert response.status_code == 202
    job_id = response.json()["id"]
    status_response = client.get(f"/api/jobs/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"
    assert status_response.json()["download_url"] == f"/api/jobs/{job_id}/download"

    download_response = client.get(f"/api/jobs/{job_id}/download")
    assert download_response.status_code == 200
    assert download_response.content.startswith(b"PK")


def test_download_rejects_unfinished_job(tmp_path, monkeypatch) -> None:
    client, session_factory = build_test_client(tmp_path, monkeypatch)
    with session_factory() as db:
        job = ReportJob(template_path="template.docx", data_path="data.csv", status="queued")
        db.add(job)
        db.commit()
        job_id = job.id

    response = client.get(f"/api/jobs/{job_id}/download")

    assert response.status_code == 409


def build_test_client(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "storage"))
    get_settings.cache_clear()
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def override_get_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), session_factory


def make_docx_bytes(tmp_path) -> bytes:
    path = tmp_path / "template.docx"
    Document().save(path)
    return path.read_bytes()
