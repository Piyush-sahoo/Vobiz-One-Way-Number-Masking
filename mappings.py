"""In-memory mapping store for one-way (destination-based) masking.

Each destination has its own dedicated masking number, one-to-one:

  M1 -> D1, M2 -> D2, M3 -> D3, ...

The mapping is resolved purely by the masking number that was dialled — the
source number is irrelevant, so *any* caller (registered or not) can use it.
Trade-off: this needs the most DIDs (one per destination), so it costs more.

All numbers are loaded from the environment (a local ``.env`` is read via
python-dotenv) as ``ONE_WAY_MAPPINGS``, a comma-separated list of
``masking:destination`` pairs. Nothing is hardcoded in source.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# masking_number -> real destination, parsed from .env. Replace the defaults.
# Format: "masking1:dest1,masking2:dest2,..."  (E.164, no '+')
_RAW = os.environ.get(
    "ONE_WAY_MAPPINGS",
    "919000000001:919876511111,919000000002:919876522222",
)

MAPPINGS: dict[str, str] = {}
for _pair in _RAW.split(","):
    if ":" in _pair:
        _m, _d = _pair.split(":", 1)
        MAPPINGS[_m.strip()] = _d.strip()


def _norm(number: str) -> str:
    """Normalise a phone number: digits only, last 10 digits. Tolerant of '+',
    spaces, leading 0, and a missing country code."""
    digits = "".join(c for c in (number or "") if c.isdigit())
    return digits[-10:] if len(digits) >= 10 else digits


# Pre-normalise keys so the lookup is format-independent.
_NORM_MAPPINGS = {_norm(k): v for k, v in MAPPINGS.items()}


def resolve(masking_number: str) -> str | None:
    """Return the destination for a masking number, or None if unknown."""
    return _NORM_MAPPINGS.get(_norm(masking_number))
