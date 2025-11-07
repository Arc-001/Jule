# Jule — Discord-driven dynamic subdomain sites

This repository contains a small Discord bot and a `SubdomainManager` helper that
creates simple HTML sites for users and (optionally) creates DNS records via the
Porkbun API.

This implementation is intentionally safe for local testing:
- By default it writes sites to `./sites/<subdomain>.info.4rc.in/index.html` (no sudo required).
- DNS creation is a no-op (dry-run) unless you set `PORKBUN_APIKEY` and `PORKBUN_SECRET`.

Files of interest
- `src/subdomain_manager.py` — core logic: sanitize, write site, (optionally) call DNS API
- `src/bot.py` — minimal Discord bot exposing `!create <html>` command
- `requirements.txt` — Python dependencies

Quick start (local, test-only)

1. Create a virtualenv and install deps (fish shell):

```fish
python -m venv .venv
. .venv/bin/activate.fish
pip install -r requirements.txt
```

2. Run unit tests:

```fish
pytest -q
```

3. Run the bot (optional)

Create a `.env` file based on `.env.example` and set `DISCORD_TOKEN`.

```fish
python -m src.bot
```

Notes & next steps
- For production use you'd want to: tighten HTML sanitization rules, add rate-limiting,
  enforce quotas, persist mappings in a database, and secure DNS and webserver operations.
- The repo writes to `./sites` by default for safety. Point `SubdomainManager(base_path=...)`
  to `/var/www/html/user-sites` when deploying on your server.
