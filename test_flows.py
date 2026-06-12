from fastapi.testclient import TestClient

import mappings
from app import app

client = TestClient(app)


def test_any_source_reaches_mapped_destination():
    masking, dest = next(iter(mappings.MAPPINGS.items()))
    # Two different (unregistered) source numbers both work.
    for src in ("910000000000", "447700900000"):
        r = client.post("/answer", data={"From": src, "To": masking})
        assert f"<Number>{dest}</Number>" in r.text
        assert f'callerId="{masking}"' in r.text


def test_unknown_masking_number_rejected():
    r = client.post("/answer", data={"From": "910000000000", "To": "910000000099"})
    assert "<Hangup" in r.text
    assert "<Dial" not in r.text
