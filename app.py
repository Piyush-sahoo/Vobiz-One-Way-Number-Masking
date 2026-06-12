"""Strategy 3 — One-way mapping (destination based).

Each destination has its own masking number. Anyone can dial the masking number
(no registration needed); the destination is resolved from the dialled number
only. Vobiz bridges using the masking number as caller ID.

Run:  uvicorn app:app --reload --port 8003
"""
from __future__ import annotations

from fastapi import FastAPI, Form, Response

import mappings
from vobiz_xml import dial, hangup, response, speak

app = FastAPI(title="Vobiz masking — one-way")

XML = "application/xml"


@app.post("/answer")
async def answer(
    From: str = Form(...),
    To: str = Form(...),
    CallUUID: str = Form(default=""),
    Direction: str = Form(default=""),
    CallStatus: str = Form(default=""),
) -> Response:
    destination = mappings.resolve(To)
    if destination is None:
        xml = response(
            speak("This masking number is not in service."),
            hangup(reason="unknown_number"),
        )
        return Response(content=xml, media_type=XML)

    # Source number is intentionally ignored — any caller is allowed.
    xml = response(dial(destination, caller_id=To, timeout=30))
    return Response(content=xml, media_type=XML)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "strategy": "one-way"}
