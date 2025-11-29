"""
Shared helper functions for evidence creation and parsing.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from ._schema import GitHubActor, GitHubRepository


def generate_evidence_id(prefix: str, *parts: str) -> str:
    """Generate a deterministic evidence ID.

    Creates a unique ID by hashing the parts and prefixing with the type.
    Same inputs always produce the same ID (idempotent).

    Args:
        prefix: Type prefix (e.g., "push", "commit", "ioc")
        *parts: Components to hash (e.g., repo name, sha, timestamp)

    Returns:
        ID in format: "{prefix}-{12-char-hash}"
    """
    content = ":".join(parts)
    hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
    return f"{prefix}-{hash_val}"


def parse_datetime_lenient(dt_str: Any) -> datetime:
    """Parse datetime from various formats, with fallback to now.

    Lenient parsing for GH Archive data where dates might be malformed.
    Returns current time if parsing fails.

    Args:
        dt_str: Datetime as string, datetime object, or None

    Returns:
        Parsed datetime (always with UTC timezone)
    """
    if dt_str is None:
        return datetime.now(timezone.utc)
    if isinstance(dt_str, datetime):
        return dt_str

    if isinstance(dt_str, str):
        # ISO format with Z
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError:
            pass

        # Try common formats
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S %Z",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue

    return datetime.now(timezone.utc)


def parse_datetime_strict(dt_str: str | datetime | None) -> datetime | None:
    """Parse datetime from various formats, strict mode.

    For verified data sources where dates should be valid.
    Raises ValueError on invalid format, returns None for None input.

    Args:
        dt_str: Datetime as string, datetime object, or None

    Returns:
        Parsed datetime or None

    Raises:
        ValueError: If date string cannot be parsed
    """
    if dt_str is None:
        return None
    if isinstance(dt_str, datetime):
        return dt_str

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S %Z",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse datetime: {dt_str}")


def make_actor(login: str, actor_id: int | None = None) -> GitHubActor:
    """Create GitHubActor from components."""
    return GitHubActor(login=login, id=actor_id)


def make_repo(owner: str, name: str) -> GitHubRepository:
    """Create GitHubRepository from owner and name."""
    return GitHubRepository(owner=owner, name=name, full_name=f"{owner}/{name}")


def make_repo_from_full_name(full_name: str) -> GitHubRepository:
    """Create GitHubRepository from full name (owner/repo format)."""
    parts = full_name.split("/", 1)
    if len(parts) == 2:
        return GitHubRepository(owner=parts[0], name=parts[1], full_name=full_name)
    return GitHubRepository(owner="unknown", name=full_name, full_name=full_name)
