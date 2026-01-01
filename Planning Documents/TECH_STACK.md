# BoosterBoxPro - Technology Stack

> **Decision Framework:** This stack prioritizes developer productivity, maintainability, and proven reliability for a data-intensive application with real-time metrics and marketplace integrations.

---

## 🎯 Stack Selection Criteria

1. **Data Processing** - Heavy emphasis on aggregations, time-series, EMAs/SMAs
2. **API Performance** - Sub-200ms response times for leaderboards
3. **Marketplace Integrations** - Multiple API adapters, rate limiting, retry logic
4. **Scalability** - Start small (10 boxes), scale to 1000+
5. **Developer Experience** - Fast iteration, good tooling, type safety
6. **Cost Efficiency** - MVP-friendly pricing, predictable scaling

---

## 📦 Backend Stack

### Core Framework

**Language:** Python 3.11+
- ✅ Excellent for data processing (pandas, numpy)
- ✅ Strong ecosystem for API integrations
- ✅ Type hints for better code quality
- ✅ Async/await support for I/O-bound operations

**Web Framework:** FastAPI
- ✅ Auto-generated OpenAPI docs (great for frontend devs)
- ✅ Async by default (handles concurrent API calls well)
- ✅ Type hints with Pydantic models
- ✅ Fast performance (comparable to Node.js)
- ✅ Built-in validation, serialization
- ✅ WebSocket support (if needed later)

**Alternative Considered:** Django (too heavy for API-only), Flask (less modern)

### ORM & Database

**Database:** PostgreSQL 15+
- ✅ Excellent for time-series data (window functions, date functions)
- ✅ JSONB support (store raw API responses)
- ✅ Strong indexing (critical for rankings)
- ✅ ACID compliance (data integrity)
- ✅ Partitioning support (for raw snapshot tables)

**ORM:** SQLAlchemy 2.0 (async)
- ✅ Async support (matches FastAPI)
- ✅ Type hints with SQLModel (optional, built on SQLAlchemy)
- ✅ Migration support via Alembic
- ✅ Mature, well-documented

**Migrations:** Alembic
- ✅ Industry standard
- ✅ Version control for schema changes
- ✅ Rollback support

### Caching

**Cache:** Redis 7+
- ✅ Fast in-memory cache (<1ms access)
- ✅ TTL support (perfect for leaderboards)
- ✅ Used by Celery for task queue (dual purpose)
- ✅ Pub/sub support (if needed for real-time updates)

**Use Cases:**
- Top 10 / Top 50 leaderboard results (5-15 min TTL)
- Individual box detail views (5 min TTL)
- API rate limiting counters
- Session storage (if using Redis sessions)

### Task Queue

**Queue:** Celery + Redis (broker)
- ✅ Async task processing (ingestion, calculations)
- ✅ Retry logic with exponential backoff
- ✅ Scheduled tasks (cron-like) via Celery Beat
- ✅ Task monitoring via Flower (optional)
- ✅ Uses Redis as broker (already in stack)

**Task Types:**
- Marketplace data ingestion (TCGplayer, eBay)
- Daily metrics calculation
- Cache warming
- Scheduled maintenance

### Authentication & Security

**JWT Library:** `python-jose[cryptography]`
- ✅ JWT encoding/decoding
- ✅ Token expiration handling
- ✅ RSA/HS256 support
- ✅ Works well with FastAPI

**Password Hashing:** `passlib[bcrypt]`
- ✅ Industry standard bcrypt
- ✅ Automatic salt generation
- ✅ Cost factor tuning

**Alternative Considered:** `argon2-cffi` (more secure, but bcrypt is simpler)

### Data Processing

**Scientific Computing:**
- `pandas` - Time-series data, aggregations, EMAs
- `numpy` - Numerical computations

**Date Handling:** `pendulum`
- ✅ Timezone-aware (critical for daily snapshots)
- ✅ Better API than datetime
- ✅ Parsing, formatting

**Alternative Considered:** `arrow` (pendulum is more powerful)

### HTTP Clients

**Requests Library:** `httpx` (async) or `requests` (sync)
- ✅ `httpx` recommended for async FastAPI
- ✅ Better than `aiohttp` (more requests-like API)
- ✅ HTTP/2 support
- ✅ Connection pooling

### Validation & Serialization

**Schema Validation:** Pydantic (built into FastAPI)
- ✅ Type validation
- ✅ Automatic serialization
- ✅ JSON Schema generation

### Logging & Monitoring

**Logging:** Python `logging` + structured logging
- ✅ Built-in, lightweight
- ✅ JSON formatter for log aggregation services

**Monitoring (Phase 2+):**
- **APM:** Sentry (error tracking) or Datadog
- **Metrics:** Prometheus + Grafana (if self-hosted)
- **Logs:** CloudWatch / Datadog Logs / ELK

**Health Checks:** Built into FastAPI (`/health` endpoint)

### Testing

**Testing Framework:** `pytest`
- ✅ Industry standard
- ✅ Fixtures, parametrization
- ✅ Async support

**Test Coverage:** `pytest-cov`
- ✅ Coverage reports
- ✅ Aim for 80%+ on critical paths

**HTTP Testing:** `httpx` (TestClient in FastAPI)
- ✅ Test API endpoints
- ✅ Async test support

**Mocking:** `pytest-mock` or `unittest.mock`
- ✅ Mock external APIs (TCGplayer, eBay)

### Development Tools

**Code Quality:**
- `black` - Code formatter
- `ruff` - Fast linter (replaces flake8, isort, etc.)
- `mypy` - Type checking

**Pre-commit Hooks:** `pre-commit`
- ✅ Auto-format, lint before commits

---

## 🗄️ Data Stack

### Database Hosting Options

**Development:**
- Local PostgreSQL (Docker Compose)
- Or: Managed service (Supabase, Neon, Railway)

**Production Options:**

1. **Supabase** (Recommended for MVP)
   - ✅ Free tier (good for MVP)
   - ✅ Managed PostgreSQL
   - ✅ Built-in auth (if we want to use it later)
   - ✅ Auto backups
   - ✅ Easy scaling

2. **AWS RDS** (Production)
   - ✅ Fully managed
   - ✅ High availability
   - ✅ Automated backups
   - ✅ More expensive

3. **Neon** (Modern alternative)
   - ✅ Serverless Postgres
   - ✅ Good free tier
   - ✅ Branching (like git for DB)

**Decision Needed:** Which hosting for Phase 1 MVP?

### Redis Hosting

**Development:**
- Local Redis (Docker Compose)

**Production Options:**

1. **Redis Cloud** (Recommended)
   - ✅ Free tier (30MB)
   - ✅ Managed
   - ✅ Easy scaling

2. **AWS ElastiCache** (Production)
   - ✅ Managed
   - ✅ More expensive
   - ✅ Better for high scale

3. **Upstash** (Serverless Redis)
   - ✅ Pay-per-use
   - ✅ Good for variable traffic

**Decision Needed:** Which hosting for Phase 1 MVP?

---

## 📱 Frontend Stack

### Mobile App (Phase 1 - MVP)

**Framework Options:**

1. **React Native** (Recommended)
   - ✅ Cross-platform (iOS + Android)
   - ✅ Large ecosystem
   - ✅ TypeScript support
   - ✅ Good performance
   - ✅ Can share code with web (React)

2. **Flutter**
   - ✅ Cross-platform
   - ✅ Excellent performance
   - ✅ Modern UI framework
   - ❌ Different language (Dart)
   - ❌ Can't share code with web

3. **Native (Swift + Kotlin)**
   - ✅ Best performance
   - ✅ Platform-specific features
   - ❌ Two codebases
   - ❌ Slower development

**Recommendation:** React Native for MVP (faster development, code sharing potential)

**State Management:** React Query / TanStack Query
- ✅ API data fetching/caching
- ✅ Automatic refetching
- ✅ Loading/error states

**Navigation:** React Navigation
- ✅ Industry standard for React Native
- ✅ Tab navigation (leaderboard, favorites, etc.)

**HTTP Client:** `axios` or `fetch`
- ✅ Simple API calls to FastAPI backend

### Website (Phase 3)

**Framework:** Next.js 14+ (React)
- ✅ Server-side rendering (SEO)
- ✅ API routes (if needed)
- ✅ Can share components/logic with React Native (if using React Native Web)
- ✅ TypeScript support

**Alternative:** Vite + React (simpler, SPA-only)

**State Management:** React Query / TanStack Query (same as mobile)

**Styling:** Tailwind CSS
- ✅ Utility-first, fast development
- ✅ Responsive design
- ✅ Dark theme support

**Charts:** Recharts or Chart.js
- ✅ Sparklines (price trends)
- ✅ Volume charts (if needed)

---

## 🚀 Deployment & Infrastructure

### Backend Hosting

**Development:**
- Local (Docker Compose)
- Or: Local virtualenv + local Postgres/Redis

**Production Options:**

1. **Railway** (Recommended for MVP)
   - ✅ Simple deployment
   - ✅ Good free tier
   - ✅ Auto-deploy from Git
   - ✅ Managed Postgres + Redis add-ons
   - ✅ Easy scaling

2. **Render**
   - ✅ Similar to Railway
   - ✅ Good free tier
   - ✅ Managed services

3. **AWS ECS / Fargate** (Production)
   - ✅ More control
   - ✅ Better for high scale
   - ✅ More complex setup

4. **Heroku** (Legacy, not recommended)
   - ⚠️ Expensive
   - ⚠️ Less modern

**Decision Needed:** Which hosting for Phase 1 MVP? (Recommend Railway or Render)

### Containerization

**Docker**
- ✅ Consistent environments
- ✅ Easy local development
- ✅ Production deployment

**Docker Compose** (Development)
- ✅ Local Postgres + Redis
- ✅ Backend API
- ✅ Celery workers
- ✅ Celery Beat scheduler

### CI/CD

**CI/CD Platform:** GitHub Actions (if using GitHub)
- ✅ Free for public repos
- ✅ Easy integration
- ✅ Run tests, linting
- ✅ Deploy to staging/production

**Pipeline Stages:**
1. Lint & type check
2. Run tests
3. Build Docker image
4. Deploy to staging (auto)
5. Deploy to production (manual approval)

**Alternative:** GitLab CI, CircleCI

---

## 🔧 Development Environment

### Local Setup

**Python Version Management:** `pyenv` or `uv`
- ✅ Multiple Python versions
- ✅ Project-specific versions

**Virtual Environment:** `venv` (built-in) or `uv`
- ✅ Isolated dependencies

**Dependency Management:** `poetry` or `pip-tools`
- ✅ `poetry` recommended (better dependency resolution)
- ✅ `pip-tools` alternative (simpler)

**Environment Variables:** `python-dotenv`
- ✅ `.env` file for local development
- ✅ Never commit secrets

**Database Migrations:** Alembic
- ✅ Version control schema
- ✅ Rollback support

### Docker Development

**Services (docker-compose.yml):**
- `postgres` - Database
- `redis` - Cache + Celery broker
- `api` - FastAPI application
- `celery-worker` - Background tasks
- `celery-beat` - Scheduled tasks

---

## 📊 Monitoring & Observability

### Phase 1 (MVP)

**Basic Logging:**
- Structured JSON logs
- Console output (development)
- File logs (production)

**Health Checks:**
- `/health` endpoint
- Database connectivity
- Redis connectivity

### Phase 2+ (Production)

**Error Tracking:**
- **Sentry** (Recommended)
  - ✅ Free tier
  - ✅ Error tracking
  - ✅ Performance monitoring
  - ✅ Release tracking

**Metrics:**
- **Prometheus + Grafana** (Self-hosted)
  - ✅ Free
  - ✅ Custom metrics
  - ✅ Dashboards

- **Datadog** (Managed)
  - ✅ All-in-one
  - ✅ More expensive

**Log Aggregation:**
- Cloud provider logs (CloudWatch, GCP Logging)
- Or: Datadog Logs
- Or: ELK Stack (self-hosted)

---

## 🔐 Security

### Authentication

**JWT Strategy:**
- Access tokens (short-lived: 1 hour)
- Optional: Refresh tokens (long-lived: 7 days)
- Stored in httpOnly cookies (web) or secure storage (mobile)

**Rate Limiting:**
- `slowapi` (FastAPI rate limiting)
- Per-IP limits (public endpoints)
- Per-user limits (authenticated endpoints)

**CORS:**
- Configured for mobile app domain
- Configured for website domain

### Secrets Management

**Development:** `.env` file (never committed)

**Production Options:**
- Environment variables (Railway, Render provide this)
- AWS Secrets Manager (if using AWS)
- HashiCorp Vault (if self-hosting)

---

## 📦 Recommended Package List

### Core Backend

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9  # PostgreSQL driver
redis==5.0.1
celery==5.3.4
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
```

### Data Processing

```txt
pandas==2.1.3
numpy==1.26.2
pendulum==3.0.0
```

### HTTP Clients

```txt
httpx==0.25.2  # Async HTTP client
```

### Testing

```txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
pytest-mock==3.12.0
httpx==0.25.2  # For TestClient
```

### Development Tools

```txt
black==23.11.0
ruff==0.1.6
mypy==1.7.1
pre-commit==3.5.0
```

### Optional (Future)

```txt
sentry-sdk==1.38.0  # Error tracking
slowapi==0.1.9  # Rate limiting
```

---

## 🎯 Stack Summary

### Backend (Locked)
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0 (async)
- **Cache:** Redis 7+
- **Queue:** Celery + Redis
- **Auth:** JWT (python-jose) + bcrypt (passlib)

### Frontend (Recommended)
- **Mobile:** React Native + TypeScript
- **Web:** Next.js 14+ (React) + TypeScript
- **State:** React Query / TanStack Query
- **Styling:** Tailwind CSS (web)

### Infrastructure (Recommended for MVP)
- **Backend Hosting:** Railway or Render
- **Database:** Supabase or Neon (managed Postgres)
- **Redis:** Redis Cloud or Upstash
- **CI/CD:** GitHub Actions

### Development
- **Containerization:** Docker + Docker Compose
- **Dependency Management:** Poetry
- **Code Quality:** black, ruff, mypy
- **Testing:** pytest

---

## ❓ Decisions Still Needed

1. **Database Hosting (MVP):** Supabase, Neon, or Railway's Postgres?
2. **Redis Hosting (MVP):** Redis Cloud, Upstash, or Railway's Redis?
3. **Backend Hosting (MVP):** Railway, Render, or other?
4. **Mobile Framework:** React Native (recommended) or Flutter?
5. **Monitoring:** Sentry for Phase 1, or defer?
6. **CI/CD:** GitHub Actions (if using GitHub)?

---

## 💰 Cost Estimate (MVP - Phase 1)

**Free Tier Friendly:**
- Railway: $5/month (after free tier)
- Supabase: Free tier (500MB database)
- Redis Cloud: Free tier (30MB)
- GitHub: Free (public repos)

**Total MVP Cost:** ~$5-10/month

**Scaling Costs (Phase 2+):**
- Database: $10-50/month (depending on size)
- Redis: $10-30/month
- Backend hosting: $20-100/month
- Monitoring: $0-26/month (Sentry free tier)

---

## 🚀 Next Steps

1. ✅ Tech stack decisions locked in
2. ⏳ Choose hosting providers (Database, Redis, Backend)
3. ⏳ Set up development environment
4. ⏳ Create project structure with recommended tools
5. ⏳ Set up Docker Compose for local development

