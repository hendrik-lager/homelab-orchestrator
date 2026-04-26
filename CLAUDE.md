# HomeLab Orchestrator - Claude.md

This project is a HomeLab Orchestrator for managing Docker hosts, Proxmox VMs, and services via a WebUI.

## Tech Stack
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) + SQLite
- **Frontend**: SvelteKit 2 + Svelte 5 + Tailwind CSS v4
- **Scheduler**: APScheduler 4.x (AsyncIOScheduler)

## Key Rules

### Async-First
- All I/O operations must use async/await
- Use `async_sessionmaker` and `AsyncSession` from SQLAlchemy 2.0
- Never use blocking calls in async context

### SSH Keys
- SSH keys must NEVER be written to disk
- Use `client_keys=[key]` parameter in asyncssh.connect()
- Keys are decrypted from Fernet-encoded database values

### Security
- All secrets encrypted with Fernet in the database
- SECRET_KEY stored in `.env` file only (chmod 600)

### Database
- SQLite WAL mode enabled: `PRAGMA journal_mode=WAL`
- Foreign keys enforced: `PRAGMA foreign_keys=ON`

### Frontend
- Svelte 5 runes: `$state`, `$derived`, `$effect`
- Tailwind v4 CSS-first: `@import "tailwindcss"` in app.css
- No JS config files for Tailwind

## Common Commands

```bash
# Install dependencies
cd backend && uv sync
cd frontend && npm install

# Run development servers
make dev-backend
make dev-frontend

# Database migrations
make migrate

# Seed test data
make seed
```

## API Endpoints
- `GET /api/v1/dashboard/summary` - Dashboard statistics
- `GET /api/v1/hosts` - List all hosts
- `GET /api/v1/services` - List all services
- `GET /api/v1/updates` - List all updates
- `GET /api/v1/alerts` - List all alerts
- `WS /api/v1/ws` - WebSocket for real-time updates
