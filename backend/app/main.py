"""PenguWave backend — application entrypoint.

This is the scaffold (Commit 1). It boots a minimal FastAPI app with a health
check so we can verify the project runs. Configuration, database, auth, and the
contract endpoints are layered on in the following commits.
"""

from fastapi import FastAPI

app = FastAPI(title="PenguWave API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe — confirms the server is up."""
    return {"status": "ok"}
