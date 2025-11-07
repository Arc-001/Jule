import asyncio
from pathlib import Path
import shutil

from src.subdomain_manager import SubdomainManager


def test_sanitize_username_edges():
    mgr = SubdomainManager(base_path=Path.cwd() / "tmp_sites_test")
    assert mgr.sanitize_username("") == "user"
    assert mgr.sanitize_username("ALICE") == "alice"
    assert mgr.sanitize_username("Alice!#$@ ") == "alice"
    assert mgr.sanitize_username("..weird..name..") == "weird-name"
    # cleanup
    shutil.rmtree(mgr.base_path)


def test_write_site_and_content(tmp_path):
    base = tmp_path / "sites"
    mgr = SubdomainManager(base_path=str(base))
    html = "<p>Hello <script>alert(1)</script> <b>World</b></p>"
    index = mgr.write_site("bob.info", html)
    assert index.exists()
    content = index.read_text(encoding="utf-8")
    # script tags should be removed by sanitizer fallback or bleach
    assert "script" not in content.lower()


def test_create_user_site_event_loop(tmp_path):
    mgr = SubdomainManager(base_path=str(tmp_path))
    async def run():
        url = await mgr.create_user_site("Charlie!!", "<p>ok</p>")
        assert url.startswith("https://charlie.info.4rc.in") or url.startswith("https://charlie.info")

    asyncio.run(run())
