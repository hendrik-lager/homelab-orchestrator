"""
Security enrichment for package updates.

Priority chain per package:
  1. Debian Security Tracker  — authoritative for Debian/PVE packages
  2. OSV (osv.dev)            — fallback for everything else
  3. Keyword heuristic        — last resort (string "security" in metadata)

Result: is_security, severity ("critical"|"high"|"medium"|"low"|"none"), cve_ids (comma-separated)
"""

import asyncio
import logging
from functools import lru_cache

import httpx

logger = logging.getLogger(__name__)

_DST_URL = "https://security-tracker.debian.org/tracker/data/json"
_OSV_URL = "https://api.osv.dev/v1/query"

# CVSS-Score → severity bucket
_CVSS_BUCKETS = [
    (9.0, "critical"),
    (7.0, "high"),
    (4.0, "medium"),
    (0.1, "low"),
]


def _cvss_to_severity(score: float | None) -> str:
    if score is None:
        return "none"
    for threshold, label in _CVSS_BUCKETS:
        if score >= threshold:
            return label
    return "none"


def _merge_severity(a: str, b: str) -> str:
    order = ["critical", "high", "medium", "low", "none"]
    return a if order.index(a) <= order.index(b) else b


# ---------------------------------------------------------------------------
# Debian Security Tracker
# ---------------------------------------------------------------------------

_dst_cache: dict | None = None
_dst_lock = asyncio.Lock()


async def _get_dst_data() -> dict:
    """Fetch and cache the full Debian Security Tracker JSON (refreshed per process)."""
    global _dst_cache
    async with _dst_lock:
        if _dst_cache is not None:
            return _dst_cache
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.get(_DST_URL)
                r.raise_for_status()
                _dst_cache = r.json()
        except Exception as exc:
            logger.warning("Debian Security Tracker nicht erreichbar: %s", exc)
            _dst_cache = {}
    return _dst_cache


async def _lookup_dst(package: str, version: str | None) -> dict | None:
    """
    Returns {"is_security": bool, "severity": str, "cve_ids": list[str]} or None.

    DST structure: {pkg: {cve: {releases: {codename: {status, urgency, ...}}}}}
    urgency values: unimportant / low / medium / high / not yet assigned
    """
    data = await _get_dst_data()
    pkg_data = data.get(package)
    if not pkg_data:
        return None

    cves: list[str] = []
    severity = "none"

    urgency_map = {
        "high": "high",
        "medium": "medium",
        "low": "low",
        "unimportant": "none",
    }

    for cve_id, cve_info in pkg_data.items():
        if not cve_id.startswith("CVE-"):
            continue
        releases = cve_info.get("releases", {})
        for release_info in releases.values():
            status = release_info.get("status", "")
            urgency = release_info.get("urgency", "")
            if status in ("resolved", "undetermined"):
                continue
            mapped = urgency_map.get(urgency, "none")
            if mapped != "none":
                cves.append(cve_id)
                severity = _merge_severity(severity, mapped)
                break

    if not cves:
        return None

    return {
        "is_security": True,
        "severity": severity,
        "cve_ids": sorted(set(cves)),
    }


# ---------------------------------------------------------------------------
# OSV fallback
# ---------------------------------------------------------------------------

async def _lookup_osv(package: str, version: str | None, ecosystem: str = "Debian") -> dict | None:
    payload: dict = {"package": {"name": package, "ecosystem": ecosystem}}
    if version:
        payload["version"] = version

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(_OSV_URL, json=payload)
            if r.status_code != 200:
                return None
            body = r.json()
    except Exception as exc:
        logger.warning("OSV nicht erreichbar: %s", exc)
        return None

    vulns = body.get("vulns", [])
    if not vulns:
        return None

    cves: list[str] = []
    severity = "none"

    for vuln in vulns:
        for alias in vuln.get("aliases", []):
            if alias.startswith("CVE-"):
                cves.append(alias)
        for sev_entry in vuln.get("severity", []):
            score_str = sev_entry.get("score", "")
            if sev_entry.get("type") == "CVSS_V3":
                try:
                    score = float(score_str.split("/")[0]) if "/" not in score_str else _parse_cvss_base(score_str)
                    severity = _merge_severity(severity, _cvss_to_severity(score))
                except (ValueError, IndexError):
                    pass

    return {
        "is_security": True,
        "severity": severity,
        "cve_ids": sorted(set(cves)),
    }


def _parse_cvss_base(vector: str) -> float:
    """Extract base score from a CVSS v3 vector string — not present in OSV responses, kept as guard."""
    return 0.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def enrich_package(
    package: str,
    version: str | None,
    *,
    hint_is_security: bool = False,
    ecosystem: str = "Debian",
) -> dict:
    """
    Returns {"is_security": bool, "severity": str, "cve_ids": str | None}

    cve_ids is a comma-separated string for storage in the DB.
    """
    result = await _lookup_dst(package, version)

    if result is None:
        result = await _lookup_osv(package, version, ecosystem=ecosystem)

    if result is None:
        # Fall back to caller-supplied hint (keyword heuristic from connector)
        if hint_is_security:
            return {"is_security": True, "severity": "low", "cve_ids": None}
        return {"is_security": False, "severity": "none", "cve_ids": None}

    cve_str = ", ".join(result["cve_ids"]) if result["cve_ids"] else None
    return {
        "is_security": result["is_security"],
        "severity": result["severity"],
        "cve_ids": cve_str,
    }


async def enrich_packages_batch(
    packages: list[dict],
    *,
    ecosystem: str = "Debian",
) -> list[dict]:
    """
    Enrich a list of package dicts in parallel.
    Each dict must have: name, current_version (optional), hint_is_security (optional).
    Returns enriched dicts with added is_security / severity / cve_ids keys.
    """
    tasks = [
        enrich_package(
            pkg["name"],
            pkg.get("current_version"),
            hint_is_security=pkg.get("is_security", False),
            ecosystem=ecosystem,
        )
        for pkg in packages
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched = []
    for pkg, res in zip(packages, results):
        out = dict(pkg)
        if isinstance(res, Exception):
            logger.warning("Enrichment fehlgeschlagen für %s: %s", pkg.get("name"), res)
            out.setdefault("severity", "none")
            out.setdefault("cve_ids", None)
        else:
            out["is_security"] = res["is_security"]
            out["severity"] = res["severity"]
            out["cve_ids"] = res["cve_ids"]
        enriched.append(out)
    return enriched
