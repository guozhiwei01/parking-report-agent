from app.services.harness import GenerationHarness


def run_generation_harness(job_id: str) -> None:
    GenerationHarness().run(job_id)
