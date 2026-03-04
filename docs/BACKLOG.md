# Newsletter Pod App — Product Backlog

> **Vision:** A personal intelligence layer for your reading — extract, summarize, chat, and discover patterns across all your newsletters and content, automatically, every day.

---

## Status Legend
- `done` — Completed
- `in-progress` — Currently being worked on
- `ready` — Ready to start, no blockers
- `backlog` — Planned but not yet ready
- `idea` — Future consideration

## Priority Legend
- `P0` — Critical / architectural blocker
- `P1` — High priority / next up
- `P2` — Medium priority
- `P3` — Nice to have
- `P4` — Idea / far future

---

# Goals & OKRs

**Goal 1: Make the daily reading experience delightful**
- KR1.1: User can view AI summaries inline in the UI (not just PDF) in <30s after fetching
- KR1.2: Content is ready when the user wakes up (automated extraction + summarization)
- KR1.3: User can navigate to any past date in the last 90 days and see summaries without re-fetching

**Goal 2: Surface patterns and intelligence across time**
- KR2.1: User can see cross-period theme reports (weekly, monthly) with zero manual effort
- KR2.2: User can ask natural-language questions about their reading history and get grounded answers
- KR2.3: Calendar view shows at-a-glance which dates have content

**Goal 3: Go beyond newsletters**
- KR3.1: At least 2 non-Gmail content sources supported (RSS, YouTube transcripts)
- KR3.2: All content sources feed into the same summary + chat + audio pipeline

**Goal 4: The system is reliable and observable enough to trust**
- KR4.1: Job run history visible in UI (last run time, success/failure, counts)
- KR4.2: API cost and token usage visible to user
- KR4.3: No silent failures — all errors logged and surfaced

---

# Epic Index

| Epic | Name | OKR | Status | Sequence |
|------|------|-----|--------|----------|
| E1 | History & Persistence | Goal 1 (KR1.3) | `ready` | Start now — architectural blocker |
| E2 | Inline Summary UI | Goal 1 (KR1.1) | `ready` | Start now — biggest UX win |
| E3 | Calendar View | Goal 1+2 (KR1.3, KR2.3) | `backlog` | After E1 |
| E4 | Cross-Period Insights | Goal 2 (KR2.1) | `backlog` | After E1+E2 |
| E5 | Chat Interface (RAG) | Goal 2 (KR2.2) | `backlog` | After E1+E2 |
| E6 | Audio Generation & Playback | Goal 1 | `backlog` | After E2 |
| E7 | Automation & Scheduling | Goal 1 (KR1.2) | `backlog` | After E2+E6 |
| E8 | Reliability & Observability | Goal 4 | `ready` | Start now — run alongside E1 |
| E9 | Content Sources Beyond Gmail | Goal 3 | `backlog` | After E6+E7 |
| E10 | Identity & Multi-User Auth | Goal 4 | `backlog` | Far future |

---

# E1 — History & Persistence

> Make the app remember. Extend newsletter retention from 10 days to 90 days, cache AI summaries so they're never regenerated unnecessarily, and expose endpoints that power the calendar and date navigation.

**OKR:** Goal 1 (KR1.3)

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E1-01 | Make newsletter retention configurable (env var), default 90 days (currently hardcoded 10-day deletion at startup) | `ready` | P0 | backend, database |
| E1-02 | Add DB index on `(owner_email, received_at)` | `ready` | P0 | backend, database |
| E1-03 | Create `summaries` table (FK to newsletter, model, tokens, cost, summary JSON, created_at) | `ready` | P0 | backend, database |
| E1-04 | PDF generation reads from `summaries` table first, only calls Claude if not cached | `backlog` | P1 | backend, ai |
| E1-05 | `GET /api/dates-with-content` — returns list of dates with newsletter data (powers calendar) | `backlog` | P1 | backend, api |
| E1-06 | `GET /api/summary/{date}` — returns stored summaries for a date | `backlog` | P1 | backend, api |
| E1-07 | Allow user to trigger re-summarization to override a cached summary | `backlog` | P2 | backend, frontend |

---

# E2 — Inline Summary UI

> Replace the PDF-only output with inline summary cards that stream progressively as Claude generates each newsletter's summary. This is the biggest UX transformation — from "download a file" to "read it here."

**OKR:** Goal 1 (KR1.1)

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E2-01 | `POST /api/summarize/{date}` — SSE endpoint that streams per-newsletter summaries as generated | `ready` | P0 | backend, api, ai |
| E2-02 | `SummaryCard.jsx` — expandable card with title, summary, key points | `ready` | P0 | frontend |
| E2-03 | Rearchitect `DailyFlow.jsx` to show summary cards inline after fetch | `ready` | P0 | frontend |
| E2-04 | Progressive SSE loading — cards appear as each summary arrives (eliminates timeout P2-15) | `backlog` | P1 | frontend, backend, ux |
| E2-05 | `ThemesBanner.jsx` — daily cross-newsletter themes banner (reuses existing `synthesize_themes()`) | `backlog` | P1 | frontend, ai |
| E2-06 | Per-newsletter expand/collapse detail view | `backlog` | P2 | frontend |
| E2-07 | "Download PDF" becomes a secondary action (not primary) | `backlog` | P2 | frontend, ux |
| E2-08 | Skeleton loading states while awaiting SSE summaries | `backlog` | P2 | frontend, ux |

---

# E3 — Calendar View

> A monthly calendar grid showing which days have content, clickable to navigate to that day's summaries. Makes the app feel like a reading history rather than a single-date tool.

**OKR:** Goal 1+2 (KR1.3, KR2.3)

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E3-01 | Add React Router (`/`, `/calendar`, `/day/:date`, `/chat`) | `backlog` | P0 | frontend, setup |
| E3-02 | `CalendarView.jsx` — monthly grid showing newsletter count per day as dot/badge | `backlog` | P0 | frontend |
| E3-03 | Calendar cells clickable → navigate to `/day/:date` and load that date's summaries | `backlog` | P0 | frontend |
| E3-04 | Month navigation (prev/next) | `backlog` | P1 | frontend |
| E3-05 | Visual differentiation: days with summaries vs newsletters-only vs empty | `backlog` | P1 | frontend, ux |
| E3-06 | Keyboard navigation across calendar grid | `backlog` | P2 | frontend, ux |
| E3-07 | Calendar heatmap variant (color intensity = newsletter count) | `backlog` | P3 | frontend, idea |

---

# E4 — Cross-Period Insights

> Run Claude over batches of stored summaries to surface weekly and monthly theme reports. "What have you been reading about this month?" — answered automatically.

**OKR:** Goal 2 (KR2.1)

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E4-01 | `insights` table: period_type, period_start, period_end, themes JSON, report_text | `backlog` | P1 | backend, database |
| E4-02 | `insights_service.py`: runs Claude over batch of stored summaries, extracts cross-period themes | `backlog` | P1 | backend, ai |
| E4-03 | `POST /api/insights/generate` — on-demand insight for a date range | `backlog` | P1 | backend, api |
| E4-04 | `GET /api/insights` — paginated stored insight reports | `backlog` | P1 | backend, api |
| E4-05 | `InsightReport.jsx` — renders cross-period report with theme breakdown | `backlog` | P1 | frontend |
| E4-06 | Weekly auto-generation (Sundays) | `backlog` | P2 | backend, automation |
| E4-07 | Monthly auto-generation (1st of month) | `backlog` | P2 | backend, automation |
| E4-08 | "Top topics this month" widget on home/dashboard | `backlog` | P2 | frontend |
| E4-09 | Topic-to-source matrix (which newsletters repeatedly cover which topics) | `backlog` | P3 | backend, ai, idea |
| E4-10 | Comparative insights ("this week vs. last week" delta) | `backlog` | P3 | backend, ai, idea |

---

# E5 — Chat Interface (RAG)

> Ask natural-language questions about your reading history. "What did I read about AI regulation last month?" — answered by retrieving relevant summaries and grounding Claude's response with citations.

**OKR:** Goal 2 (KR2.2)

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E5-01 | Evaluate vector store (sqlite-vec, Chroma, Pinecone) — start with sqlite-vec | `backlog` | P1 | backend, ai |
| E5-02 | `embedding_service.py`: generate and store embeddings for each newsletter summary | `backlog` | P1 | backend, ai |
| E5-03 | `vectors` table (newsletter_id, embedding, chunk_text) | `backlog` | P1 | backend, database |
| E5-04 | Auto-embed summaries on write | `backlog` | P1 | backend, ai |
| E5-05 | `chat_service.py`: query embedding → retrieve top-k → Claude with context → streamed response | `backlog` | P1 | backend, ai |
| E5-06 | `POST /api/chat/message` endpoint | `backlog` | P1 | backend, api |
| E5-07 | `chat_history` table: conversation_id, role, message, created_at | `backlog` | P2 | backend, database |
| E5-08 | `ChatView.jsx` — chat UI with message input, history, source citations | `backlog` | P1 | frontend |
| E5-09 | Chat route at `/chat` | `backlog` | P1 | frontend |
| E5-10 | Source citation display: each answer shows which newsletters it drew from with date | `backlog` | P1 | frontend, ux |
| E5-11 | Date-scoped queries ("in the last week") | `backlog` | P2 | backend, ai |
| E5-12 | Suggested starter questions shown on empty chat | `backlog` | P2 | frontend, ux |
| E5-13 | Backfill embeddings for all existing stored summaries (one-time migration) | `backlog` | P1 | backend, database |

---

# E6 — Audio Generation & Playback

> Turn daily summaries into a listenable podcast episode. TTS generation, an in-app audio player, and download support.

**OKR:** Goal 1

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E6-01 | Integrate TTS engine (Google Cloud TTS or ElevenLabs) | `ready` | P0 | backend, audio |
| E6-02 | Voice selection and configuration | `backlog` | P1 | backend, audio |
| E6-03 | Audio processing (normalization, pauses, chapters) | `backlog` | P1 | backend, audio |
| E6-04 | MP3 file generation and storage | `backlog` | P0 | backend, audio |
| E6-05 | `POST /api/generate-podcast` — create audio from script | `backlog` | P0 | backend, api |
| E6-06 | `GET /api/podcasts` — list all podcasts | `backlog` | P0 | backend, api |
| E6-07 | `GET /api/podcasts/{id}/stream` — stream audio file | `backlog` | P0 | backend, api |
| E6-08 | `GET /api/podcasts/{id}/download` — download audio | `backlog` | P1 | backend, api |
| E6-09 | Podcasts database table | `backlog` | P0 | backend, database |
| E6-10 | PodcastNewsletter junction table | `backlog` | P1 | backend, database |
| E6-11 | Audio player component in frontend | `backlog` | P0 | frontend |
| E6-12 | Play, pause, skip controls | `backlog` | P0 | frontend |
| E6-13 | Progress bar with timestamp | `backlog` | P0 | frontend |
| E6-14 | Playback speed control (0.75x – 2x) | `backlog` | P1 | frontend |
| E6-15 | Chapter navigation (jump to newsletter) | `backlog` | P2 | frontend |
| E6-16 | Download button | `backlog` | P2 | frontend |
| E6-17 | File cleanup for old audio files (>30 days) | `backlog` | P2 | backend |

---

# E7 — Automation & Scheduling

> Make the app run itself. Daily extraction, summarization, and podcast generation happen before the user wakes up — no manual trigger required.

**OKR:** Goal 1 (KR1.2)

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E7-01 | Set up task scheduler (APScheduler or Celery) | `backlog` | P0 | backend, automation |
| E7-02 | Daily extraction task at 5:30 AM | `backlog` | P0 | backend, automation |
| E7-03 | Automatic parsing after extraction | `backlog` | P0 | backend, automation |
| E7-04 | Automatic summarization and audio generation | `backlog` | P0 | backend, automation |
| E7-05 | Error handling and retry logic | `backlog` | P1 | backend, automation |
| E7-06 | Email notification when content is ready | `backlog` | P2 | backend, notification |
| E7-07 | New content notification indicator in UI | `backlog` | P2 | frontend |
| E7-08 | Weekly insights auto-generation (Sundays) | `backlog` | P2 | backend, automation |
| E7-09 | User preferences: default categories, voice, playback speed, notification opt-in | `backlog` | P1 | backend, frontend |
| E7-10 | Settings page in frontend | `backlog` | P1 | frontend |

---

# E8 — Reliability & Observability

> Make the system trustworthy. Surface job run history, API costs, and errors in the UI so silent failures are impossible.

**OKR:** Goal 4 (KR4.1, KR4.2, KR4.3)

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E8-01 | `GET /api/system/status` — last job run times, success/failure, newsletter counts | `ready` | P0 | backend, api |
| E8-02 | Status banner in UI ("Last extraction: today 6:02 AM — 8 newsletters") | `ready` | P0 | frontend |
| E8-03 | API cost dashboard: Claude spend this month, breakdown by date | `backlog` | P1 | backend, frontend |
| E8-04 | Structured JSON logging throughout backend | `backlog` | P1 | backend |
| E8-05 | Gmail token expiry detection with graceful warning in UI | `backlog` | P1 | backend, frontend, gmail |
| E8-06 | `GET /api/system/jobs` — job run history from `job_runs` table | `backlog` | P1 | backend, api |
| E8-07 | Health check endpoint (DB, Gmail token, Claude API) | `backlog` | P1 | backend, api |
| E8-08 | Alert when newsletter count is unexpectedly low | `backlog` | P2 | backend |
| E8-09 | Parsing failure rate tracking (surface warning if >20% fail) | `backlog` | P2 | backend, frontend |
| E8-10 | Automated daily DB backup in production | `backlog` | P2 | backend |

---

# E9 — Content Sources Beyond Gmail

> Generalize the pipeline to ingest RSS feeds and YouTube transcripts, making Gmail one source among many.

**OKR:** Goal 3 (KR3.1, KR3.2)

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E9-01 | Generalize schema: `source_type` field on content table (newsletter, rss_article, youtube_transcript) | `backlog` | P1 | backend, database |
| E9-02 | `rss_service.py`: poll RSS feeds, store as content items | `backlog` | P1 | backend |
| E9-03 | User-configurable RSS feed list in settings UI | `backlog` | P1 | backend, frontend |
| E9-04 | `youtube_service.py`: fetch transcript via youtube-transcript-api | `backlog` | P2 | backend |
| E9-05 | RSS extraction scheduled job | `backlog` | P2 | backend, automation |
| E9-06 | All source types feed same summarization pipeline | `backlog` | P1 | backend, ai |
| E9-07 | All source types retrievable in chat | `backlog` | P1 | backend, ai |
| E9-08 | Twitter/X thread support | `backlog` | P3 | backend, idea |

---

# E10 — Identity & Multi-User Auth

> Replace developer-configured OAuth with "Login with Gmail" so any user can connect their own inbox. Requires Privacy Policy, Terms of Service, and per-user data isolation.

**OKR:** Goal 4

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| E10-01 | Multi-user support with authentication | `backlog` | P1 | backend, auth |
| E10-02 | Per-user Gmail connections (replace pickle with per-user refresh tokens in DB) | `backlog` | P1 | backend, gmail, auth |
| E10-03 | "Login with Gmail" OAuth consent screen + user profile | `backlog` | P2 | backend, auth, gmail, frontend |
| E10-04 | Privacy Policy and Terms of Service pages (required for Google OAuth verification) | `backlog` | P2 | frontend |
| E10-05 | PostgreSQL migration for multi-user scalability | `backlog` | P2 | backend, database |

---

# Future Ideas

Ideas not yet assigned to an epic — preserved for later prioritization.

| ID | Idea | Priority | Labels |
|----|------|----------|--------|
| FUT-01 | Personalized summaries based on user interests | P2 | ai, personalization |
| FUT-02 | Track engagement (clicks, time spent) for personalization | P3 | personalization |
| FUT-03 | Thumbs up/down feedback on summaries | P2 | personalization, frontend |
| FUT-04 | Explicit interest settings ("more AI, less fundraising") | P3 | personalization |
| FUT-05 | Learn preferred summary length/detail level | P3 | personalization, ai |
| FUT-06 | Remember read topics to avoid repetition | P3 | personalization |
| FUT-07 | Weight trusted sources more heavily | P3 | personalization |
| FUT-08 | Native iOS app | P3 | mobile |
| FUT-09 | Native Android app | P3 | mobile |
| FUT-10 | Offline playback support | P3 | mobile |
| FUT-11 | CarPlay / Android Auto integration | P4 | mobile |
| FUT-12 | Spotify/Apple Podcasts distribution | P3 | distribution |
| FUT-13 | RSS feed generation (publish your summaries as a feed) | P3 | distribution |
| FUT-14 | Notion integration for highlights | P3 | integration |
| FUT-15 | Readwise integration | P3 | integration |
| FUT-16 | Trello/Notion backlog sync | P4 | tooling |
| FUT-17 | Parallel AI processing optimization (batching + rate limit management) | P2 | backend, ai, performance |
| FUT-18 | Progressive Web App (PWA) support | P3 | frontend |
| FUT-19 | Dark mode | P3 | frontend |
| FUT-20 | Mobile-responsive design improvements | P2 | frontend |
| FUT-21 | Keyboard shortcuts | P3 | frontend, ux |
| FUT-22 | Batch processing for large volumes | P2 | backend |

---

# Done — Completed Items Archive

All items completed in the original Phase 0–2 work. Preserved for reference.

## Foundation & Setup (Phase 0)

| ID | Task | Labels |
|----|------|--------|
| P0-01 | Initialize GitHub repo with README and .gitignore | setup |
| P0-02 | Create project directory structure (/backend, /frontend, /parsers, /docs) | setup |
| P0-03 | Set up requirements.txt with dependencies | setup |
| P0-04 | Create .env.example for environment variables | setup |
| P0-05 | Migrate existing parser code to /parsers | setup |

## Core Backend & Basic UI (Phase 1)

| ID | Task | Labels |
|----|------|--------|
| P1-01 | Set up FastAPI backend with CORS | backend |
| P1-02 | Create SQLite database with SQLAlchemy ORM | backend, database |
| P1-03 | Create Newsletter model with all fields | backend, database |
| P1-04 | Implement Gmail OAuth 2.0 authentication | backend, gmail |
| P1-05 | `GET /api/newsletters` — list parsed newsletters | backend, api |
| P1-06 | `GET /api/newsletters/{id}` — get newsletter details | backend, api |
| P1-07 | `POST /api/extract` — trigger email extraction | backend, api |
| P1-08 | `GET /api/categories` — list categories with counts | backend, api |
| P1-09 | `GET /api/stats` — overall statistics | backend, api |
| P1-10 | Multi-platform parser (Substack, Beehiiv, TLDR, ConvertKit, Generic) | parser |
| P1-11 | Newsletter auto-categorization by sender | parser |
| P1-12 | Content validation (min length, sentence structure) | parser |
| P1-13 | React frontend with Vite setup | frontend |
| P1-14 | Newsletter list view with cards | frontend |
| P1-15 | Newsletter detail view | frontend |
| P1-16 | Category and date filtering | frontend |
| P1-17 | "Extract Newsletters" button | frontend |

## AI Summarization (Phase 2)

| ID | Task | Labels |
|----|------|--------|
| P2-01 | Integrate Anthropic Claude API | backend, ai |
| P2-02 | Create summarization service module | backend, ai |
| P2-03 | Implement per-category AI summarization | backend, ai |
| P2-04 | Add token usage and cost logging | backend, ai |
| P2-05 | `GET /api/ai-summary` — daily AI summaries by category | backend, api |
| P2-06 | `GET /api/newsletters/{id}/ai-summary` — single newsletter AI summary | backend, api |
| P2-07 | `GET /api/daily-briefing` — podcast-style script | backend, api |
| P2-08 | Summary view in frontend with AI toggle | frontend |
| P2-09 | "Generate Podcast Script" button | frontend |
| P2-10 | Display briefing/script in UI | frontend |
| P2-11 | Local timezone handling for date filtering | backend |
| P2-17 | Remove category grouping from AI summary, use flat newsletter list | backend, api |
| P2-18 | PDF export of daily newsletter summary with overlapping themes | backend, api, frontend |

---

# Quick Stats

| Epic | Total | Done | In Progress | Ready | Backlog |
|------|-------|------|-------------|-------|---------|
| E1 — History & Persistence | 7 | 0 | 0 | 3 | 4 |
| E2 — Inline Summary UI | 8 | 0 | 0 | 3 | 5 |
| E3 — Calendar View | 7 | 0 | 0 | 0 | 7 |
| E4 — Cross-Period Insights | 10 | 0 | 0 | 0 | 10 |
| E5 — Chat Interface (RAG) | 13 | 0 | 0 | 0 | 13 |
| E6 — Audio Generation & Playback | 17 | 0 | 0 | 1 | 16 |
| E7 — Automation & Scheduling | 10 | 0 | 0 | 0 | 10 |
| E8 — Reliability & Observability | 10 | 0 | 0 | 2 | 8 |
| E9 — Content Sources Beyond Gmail | 8 | 0 | 0 | 0 | 8 |
| E10 — Identity & Multi-User Auth | 5 | 0 | 0 | 0 | 5 |
| Future Ideas | 22 | — | — | — | 22 |
| **Done Archive** | **35** | **35** | — | — | — |

**New items:** 95 across 10 epics
**Completed (archived):** 35 items
**Total in system:** 130

---

# Prioritization Recommendation

**Start now — architectural blockers (this sprint):**
- E1-01: Extend retention to 90 days — one-line env var change, losing history every day we wait
- E1-02: DB index on `(owner_email, received_at)`
- E1-03: `summaries` table
- E8-01: `GET /api/system/status`
- E8-02: Status banner in UI

**Near-term — biggest UX wins (next 1-2 months):**
- E2-01 through E2-05: Inline summaries + SSE streaming (eliminates PDF-only flow)
- E3-01 through E3-03: Routing setup + calendar view

**Medium-term (2-4 months):**
- E4: Cross-period insights
- E7: Automation / scheduling
- E6: Audio generation

**Later:**
- E5: Chat / RAG — most complex, needs E1+E2+embeddings first
- E9: Additional content sources
- E10: Auth — only needed for multi-user hosting

---

# Labels Reference

| Label | Description |
|-------|-------------|
| `setup` | Initial project setup |
| `backend` | Python/FastAPI backend work |
| `frontend` | React frontend work |
| `database` | Database schema/queries |
| `api` | REST API endpoints |
| `parser` | Newsletter parsing logic |
| `gmail` | Gmail API integration |
| `ai` | Claude API / AI features |
| `audio` | TTS / audio generation |
| `automation` | Scheduling / background tasks |
| `notification` | Alerts / notifications |
| `personalization` | User preference learning |
| `ux` | User experience improvements |
| `auth` | Authentication / identity |
| `mobile` | Mobile app features |
| `distribution` | Podcast distribution |
| `integration` | Third-party integrations |
| `performance` | Performance optimization |
| `tooling` | Development tools |
| `idea` | Speculative / future consideration |
