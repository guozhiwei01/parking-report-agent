import logging

from fastapi import FastAPI

from app.api.jobs import router as jobs_router

logging.basicConfig(level=logging.INFO, format="%(message)s")

app = FastAPI(title="Parking Report Agent")
app.include_router(jobs_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
