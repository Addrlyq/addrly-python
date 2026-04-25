"""Addrly API client."""

from __future__ import annotations

import requests
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote


class AddrlyError(Exception):
    """Error returned by the Addrly API."""

    def __init__(self, status: int, error: str, response: Optional[Dict] = None):
        self.status = status
        self.error = error
        self.response = response
        super().__init__(error)


class Addrly:
    """Official Addrly API client.

    Usage::

        from addrly import Addrly

        client = Addrly("sk_your_api_key")
        result = client.validate_email("test@gmail.com")
        print(result["mx"], result["disposable"])
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.addrly.app",
        timeout: int = 30,
    ):
        if not api_key:
            raise ValueError("Addrly: API key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        })

    # ── Email Validation ─────────────────────────────────

    def validate_email(
        self, email: str, *, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate a single email address."""
        body: Dict[str, Any] = {"email": email}
        if environment:
            body["environment"] = environment
        return self._post("/api/v1/email", body)

    def validate_domain(
        self, domain: str, *, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate a single domain."""
        params = {}
        if environment:
            params["environment"] = environment
        return self._get(f"/api/v1/domain/{quote(domain, safe='')}", params=params)

    def validate(
        self, input: str, *, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Auto-detect: validate email or domain."""
        if "@" in input:
            return self.validate_email(input, environment=environment)
        return self.validate_domain(input, environment=environment)

    # ── Bulk Validation ──────────────────────────────────

    def bulk_validate_emails(
        self, emails: List[str], *, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate multiple emails (Pro: max 500, Ultra: max 1000)."""
        body: Dict[str, Any] = {"emails": emails}
        if environment:
            body["environment"] = environment
        return self._post("/api/v1/bulk-email", body)

    def bulk_validate_domains(
        self, domains: List[str], *, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate multiple domains (Pro: max 500, Ultra: max 1000)."""
        body: Dict[str, Any] = {"domains": domains}
        if environment:
            body["environment"] = environment
        return self._post("/api/v1/bulk-domain", body)

    # ── Gates ────────────────────────────────────────────

    def gate(
        self,
        gate_id: str,
        *,
        email: Optional[str] = None,
        domain: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate an email or domain against a gate."""
        body: Dict[str, Any] = {}
        if email:
            body["email"] = email
        if domain:
            body["domain"] = domain
        if ip:
            body["ip"] = ip
        return self._post(f"/api/v1/gates/{quote(gate_id, safe='')}/decide", body)

    # ── HTTP ─────────────────────────────────────────────

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", path, json=body)

    def _get(
        self, path: str, params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        return self._request("GET", path, params=params)

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            resp = self._session.request(
                method, url, timeout=self._timeout, **kwargs
            )
        except requests.Timeout:
            raise AddrlyError(408, "Request timed out")
        except requests.ConnectionError as e:
            raise AddrlyError(0, f"Connection error: {e}")

        try:
            data = resp.json()
        except ValueError:
            raise AddrlyError(resp.status_code, f"Invalid JSON response (HTTP {resp.status_code})")

        if not resp.ok:
            raise AddrlyError(
                resp.status_code,
                data.get("error", f"HTTP {resp.status_code}"),
                response=data,
            )

        return data
