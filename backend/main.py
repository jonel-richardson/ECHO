"""N1 — FastAPI entry point. Thin wrapper around run_pipeline."""

import dataclasses
import logging
from http import HTTPStatus
from typing import Dict, Tuple

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.orchestrator import OrchestratorError, run_pipeline
from backend.schemas import PatientProfile


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ECHO", version="2.0")

# Demo Day CORS: deliberately permissive so frontend/index.html can hit the API
# from any origin without preflight friction. Lock these down for production
# (specific origin allowlist, narrower methods/headers).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _classify_orchestrator_error(message: str) -> Tuple[int, str, str]:
    """Map an OrchestratorError message to (http_status, client_type_label, log_subtype).

    The client_type_label is what the frontend sees and dispatches on. The
    log_subtype is server-only and lets us distinguish, in logs, between
    different internal_error conditions (e.g., missing env var vs unknown).
    """
    lowered = message.lower()
    if "longer than expected" in lowered:
        return HTTPStatus.GATEWAY_TIMEOUT, "timeout", "subagent_or_api_timeout"
    if "anthropic" in lowered:
        return HTTPStatus.BAD_GATEWAY, "upstream_error", "anthropic_api_error"
    if "missing required env var" in lowered or "anthropic_api_key" in lowered:
        return HTTPStatus.INTERNAL_SERVER_ERROR, "internal_error", "missing_env_var"
    if "missing field" in lowered or "empty" in lowered or "validation" in lowered:
        return HTTPStatus.BAD_REQUEST, "validation", "post_construction_validation"
    return HTTPStatus.INTERNAL_SERVER_ERROR, "internal_error", "unknown"


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    # FastAPI default is 422; we surface request-body failures as 400 with the
    # standard {"error", "type"} envelope to match the OrchestratorError path.
    parts = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", ()) if x != "body")
        msg = err.get("msg", "invalid")
        parts.append(f"{loc}: {msg}" if loc else msg)
    detail = "; ".join(parts) if parts else "Invalid request body."
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={"error": f"Invalid PatientProfile: {detail}", "type": "validation"},
    )


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/generate-checklist")
async def generate_checklist_endpoint(profile: PatientProfile) -> JSONResponse:
    try:
        checklist = await run_pipeline(profile)
    except OrchestratorError as exc:
        status_code, client_type, log_subtype = _classify_orchestrator_error(str(exc))
        logger.warning(
            "Orchestrator failure: client_type=%s log_subtype=%s message=%s",
            client_type, log_subtype, exc,
        )
        return JSONResponse(
            status_code=status_code,
            content={"error": str(exc), "type": client_type},
        )
    except Exception:
        logger.exception("Unhandled exception in /generate-checklist")
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error.", "type": "internal_error"},
        )

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=dataclasses.asdict(checklist),
    )
