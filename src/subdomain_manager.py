"""Subdomain manager: creates site directories, writes sanitized HTML, and (optionally)
creates DNS records via Porkbun API.

Design notes:
- Non-privileged by default: writes to a configurable base_path (defaults to ./sites)
- DNS integration is optional and runs only if PORKBUN_APIKEY and PORKBUN_SECRET are provided
- HTML sanitization uses bleach if available, otherwise falls back to a conservative strip
"""
from pathlib import Path
import os
import json
import re
from typing import Optional


class SubdomainManager:
    def __init__(self, base_path: Optional[str] = None, server_ip: Optional[str] = None):
        # Default to a local `sites` folder for safe, unprivileged testing
        self.base_path = Path(base_path or Path.cwd() / "sites")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.server_ip = server_ip or os.environ.get("SERVER_IP", "127.0.0.1")
        self.porkbun_api_key = os.environ.get("PORKBUN_APIKEY")
        self.porkbun_secret = os.environ.get("PORKBUN_SECRET")

    def sanitize_username(self, username: str) -> str:
        """Sanitize a Discord username into a valid subdomain label.

        Lowercase, keep alnum and hyphen. Collapse runs of invalid chars into a single hyphen.
        Trim leading/trailing hyphens and limit length to 63.
        """
        if not username:
            return "user"
        s = username.lower()
        # replace spaces and invalid chars with hyphen
        s = re.sub(r"[^a-z0-9-]", "-", s)
        # collapse multiple hyphens
        s = re.sub(r"-+", "-", s)
        s = s.strip("-")
        if not s:
            s = "user"
        return s[:63]

    def sanitize_html(self, html: str) -> str:
        """Sanitize HTML. Prefer bleach if available; otherwise strip scripts and inline event handlers.

        This is intentionally conservative. For production use, configure bleach with
        a strict allowlist suited to your use-case.
        """
        if html is None:
            return ""
        try:
            import bleach

            # allow a safe short list
            allowed_tags = [
                "a",
                "b",
                "i",
                "u",
                "p",
                "br",
                "strong",
                "em",
                "ul",
                "ol",
                "li",
                "code",
                "pre",
                "span",
                "div",
            ]
            allowed_attrs = {"a": ["href", "rel", "target"], "span": ["style"], "div": ["style"]}
            cleaned = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)
            return cleaned
        except Exception:
            # Fallback: naive removal of script/style tags and on* attributes
            cleaned = re.sub(r"(?is)<script.*?>.*?</script>", "", html)
            cleaned = re.sub(r"(?is)<style.*?>.*?</style>", "", cleaned)
            # remove on* attributes like onclick=
            cleaned = re.sub(r"\son\w+\s*=\s*\"[^\"]*\"", "", cleaned)
            cleaned = re.sub(r"\son\w+\s*=\s*'[^']*'", "", cleaned)
            return cleaned

    def site_path_for(self, subdomain_label: str) -> Path:
        # e.g. alice.info.4rc.in -> folder name alice.info.4rc.in
        name = f"{subdomain_label}.info.4rc.in" if not subdomain_label.endswith(".info.4rc.in") else subdomain_label
        return self.base_path / name

    def write_site(self, subdomain_label: str, html_content: str) -> Path:
        site_dir = self.site_path_for(subdomain_label)
        site_dir.mkdir(parents=True, exist_ok=True)
        index = site_dir / "index.html"
        index.write_text(self.sanitize_html(html_content), encoding="utf-8")
        # set permissive but safe perms for local testing
        try:
            os.chmod(site_dir, 0o755)
            os.chmod(index, 0o644)
        except Exception:
            # ignore permission errors on platforms where this isn't relevant
            pass
        return index

    async def create_dns_record(self, label: str) -> dict:
        """Create DNS record via Porkbun API when keys are present.

        If PORKBUN_APIKEY/PORKBUN_SECRET are not set, return a dry-run response.
        The API call is lazy-imported to avoid requiring aiohttp at import time.
        """
        if not (self.porkbun_api_key and self.porkbun_secret):
            return {"status": "dry-run", "message": "Porkbun credentials not configured"}

        # Lazy import
        try:
            import aiohttp
        except Exception as e:
            return {"status": "error", "message": f"aiohttp not available: {e}"}

        domain = "4rc.in"
        # Porkbun wants name without the registered domain; agent.md used username.info
        # We'll follow that convention: label is like 'alice' or 'alice.info'
        name = label
        url = f"https://porkbun.com/api/json/v3/dns/create/{domain}"
        payload = {
            "apikey": self.porkbun_api_key,
            "secretapikey": self.porkbun_secret,
            "name": name,
            "type": "A",
            "content": self.server_ip,
            "ttl": "300",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                return data

    async def create_user_site(self, username: str, html_content: str) -> str:
        """Top-level convenience method. Returns the full subdomain.

        Flow:
        - sanitize username -> label
        - write site to disk
        - attempt DNS creation if credentials present (non-blocking for disk ops)
        """
        label = self.sanitize_username(username)
        # agent.md suggested subdomain like username.info.4rc.in; we will create label "username.info"
        # to produce name "username.info.4rc.in" in the folder and DNS
        dn_label = f"{label}.info"
        self.write_site(dn_label, html_content)
        dns_result = await self.create_dns_record(label + ".info")
        # return URL
        url = f"https://{label}.info.4rc.in"
        return url


if __name__ == "__main__":
    # quick manual test helper
    import asyncio

    mgr = SubdomainManager()

    async def run():
        url = await mgr.create_user_site("Alice!# ", "<p>Hello <script>alert(1)</script> world</p>")
        print("site created at", url)

    asyncio.run(run())
