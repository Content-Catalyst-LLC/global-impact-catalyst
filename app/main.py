"""Application-facing wrapper for Global Impact Catalyst.

This module deliberately avoids a required web framework so repository tests can
run in minimal environments. A future Flask/FastAPI layer can call
`build_demo_response` directly.
"""

from __future__ import annotations

from python.global_impact_core import build_impact_record, input_from_dict, record_to_dict


def build_demo_response(payload: dict) -> dict:
    """Return a serializable impact record from a dictionary payload."""
    record = build_impact_record(input_from_dict(payload))
    return record_to_dict(record)


def healthcheck() -> dict:
    return {"status": "ok", "module": "global-impact-catalyst"}
