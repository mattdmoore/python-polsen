"""Versioned route builders for the Polsen Health API.

The subpackages expose pure functions that assemble request paths and contain
no HTTP logic; :mod:`python_polsen.api.v1` mirrors the ``v1`` paths described in
``openapi.json``.
"""

from __future__ import annotations

from . import v1

__all__ = ["v1"]
