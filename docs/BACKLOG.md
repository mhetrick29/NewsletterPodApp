# Newsletter Podcast Agent - Product Backlog

> Structured for Kanban/Trello/Notion integration. Each item has ID, status, priority, and labels.

---

## Status Legend
- `done` - Completed
- `in-progress` - Currently being worked on
- `ready` - Ready to start, no blockers
- `backlog` - Planned but not yet ready
- `idea` - Future consideration

## Priority Legend
- `P0` - Critical / Must have
- `P1` - High priority
- `P2` - Medium priority
- `P3` - Nice to have

---

# Phase 0: Foundation & Setup

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| P0-01 | Initialize GitHub repo with README and .gitignore | `done` | P0 | setup |
| P0-02 | Create project directory structure (/backend, /frontend, /parsers, /docs) | `done` | P0 | setup |
| P0-03 | Set up requirements.txt with dependencies | `done` | P0 | setup |
| P0-04 | Create .env.example for environment variables | `done` | P0 | setup |
| P0-05 | Migrate existing parser code to /parsers | `done` | P0 | setup |

---

# Phase 1: Core Backend & Basic UI

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| P1-01 | Set up FastAPI backend with CORS | `done` | P0 | backend |
| P1-02 | Create SQLite database with SQLAlchemy ORM | `done` | P0 | backend, database |
| P1-03 | Create Newsletter model with all fields | `done` | P0 | backend, database |
| P1-04 | Implement Gmail OAuth 2.0 authentication | `done` | P0 | backend, gmail |
| P1-05 | GET /api/newsletters - List parsed newsletters | `done` | P0 | backend, api |
| P1-06 | GET /api/newsletters/{id} - Get newsletter details | `done` | P0 | backend, api |
| P1-07 | POST /api/extract - Trigger email extraction | `done` | P0 | backend, api |
| P1-08 | GET /api/categories - List categories with counts | `done` | P1 | backend, api |
| P1-09 | GET /api/stats - Overall statistics | `done` | P2 | backend, api |
| P1-10 | Multi-platform parser (Substack, Beehiiv, TLDR, ConvertKit, Generic) | `done` | P0 | parser |
| P1-11 | Newsletter auto-categorization by sender | `done` | P0 | parser |
| P1-12 | Content validation (min length, sentence structure) | `done` | P1 | parser |
| P1-13 | React frontend with Vite setup | `done` | P0 | frontend |
| P1-14 | Newsletter list view with cards | `done` | P0 | frontend |
| P1-15 | Newsletter detail view | `done` | P0 | frontend |
| P1-16 | Category and date filtering | `done` | P1 | frontend |
| P1-17 | "Extract Newsletters" button | `done` | P0 | frontend |

---

# Phase 2: AI Summarization & Script Generation

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| P2-01 | Integrate Anthropic Claude API | `done` | P0 | backend, ai |
| P2-02 | Create summarization service module | `done` | P0 | backend, ai |
| P2-03 | Implement per-category AI summarization | `done` | P0 | backend, ai |
| P2-04 | Add token usage and cost logging | `done` | P1 | backend, ai |
| P2-05 | GET /api/ai-summary - Daily AI summaries by category | `done` | P0 | backend, api |
| P2-06 | GET /api/newsletters/{id}/ai-summary - Single newsletter AI summary | `done` | P1 | backend, api |
| P2-07 | GET /api/daily-briefing - Podcast-style script | `done` | P0 | backend, api |
| P2-08 | Summary view in frontend with AI toggle | `done` | P0 | frontend |
| P2-09 | "Generate Podcast Script" button | `done` | P0 | frontend |
| P2-10 | Display briefing/script in UI | `done` | P0 | frontend |
| P2-11 | Local timezone handling for date filtering | `done` | P1 | backend |
| P2-12 | Prompt templates for different newsletter types | `backlog` | P2 | backend, ai |
| P2-13 | Summary quality validation | `backlog` | P2 | backend, ai |
| P2-14 | Edit/regenerate summary capability | `backlog` | P2 | frontend |
| P2-15 | **Stream AI summaries as they're generated** | `ready` | P1 | frontend, backend, ux |
|       | _Currently frontend waits for all summaries to complete, which can take 3-5 minutes for multiple categories with delays between them. User encounters `AxiosError: timeout of 120000ms exceeded` (ECONNABORTED) when processing takes longer than expected. **Workaround applied**: Increased timeout to 5 minutes (300s) in frontend/backend. **Proper solution**: Implement progressive/streaming display using WebSocket or Server-Sent Events (SSE) to show each newsletter summary as it's generated, then category rollup when complete. This will eliminate timeout issues and greatly improve perceived performance and user experience._ | | | |
| P2-16 | **User-defined newsletter categories** | `backlog` | P2 | backend, frontend |
|       | _Replace hardcoded CATEGORY_MAPPING with user-configurable categories. Allow users to create, rename, and assign newsletters to custom categories via the UI. Current hardcoded categories (product_ai, health_fitness, finance, sahil_bloom) removed from AI summary flow; category grouping should be re-introduced as an opt-in user feature._ | | | |
| P2-17 | Remove category grouping from AI summary, use flat newsletter list | `done` | P1 | backend, api |
| P2-18 | PDF export of daily newsletter summary with overlapping themes | `done` | P1 | backend, api, frontend |

---

# Phase 3: Audio Generation & Playback

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| P3-01 | Integrate TTS engine (Google Cloud TTS or ElevenLabs) | `ready` | P0 | backend, audio |
| P3-02 | Voice selection and configuration | `backlog` | P1 | backend, audio |
| P3-03 | Audio processing (normalization, pauses, chapters) | `backlog` | P1 | backend, audio |
| P3-04 | MP3 file generation and storage | `backlog` | P0 | backend, audio |
| P3-05 | POST /api/generate-podcast - Create audio from script | `backlog` | P0 | backend, api |
| P3-06 | GET /api/podcasts - List all podcasts | `backlog` | P0 | backend, api |
| P3-07 | GET /api/podcasts/{id}/stream - Stream audio file | `backlog` | P0 | backend, api |
| P3-08 | GET /api/podcasts/{id}/download - Download audio | `backlog` | P1 | backend, api |
| P3-09 | Podcasts database table | `backlog` | P0 | backend, database |
| P3-10 | PodcastNewsletter junction table | `backlog` | P1 | backend, database |
| P3-11 | Audio player component in frontend | `backlog` | P0 | frontend |
| P3-12 | Play, pause, skip controls | `backlog` | P0 | frontend |
| P3-13 | Progress bar with timestamp | `backlog` | P0 | frontend |
| P3-14 | Playback speed control (0.75x - 2x) | `backlog` | P1 | frontend |
| P3-15 | Chapter navigation (jump to category) | `backlog` | P2 | frontend |
| P3-16 | Download button | `backlog` | P2 | frontend |
| P3-17 | File cleanup for old podcasts (>30 days) | `backlog` | P2 | backend |

---

# Phase 4: Automation & Scheduling

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| P4-01 | Set up task scheduler (APScheduler or Celery) | `backlog` | P0 | backend, automation |
| P4-02 | Daily extraction task at 5:30 AM | `backlog` | P0 | backend, automation |
| P4-03 | Automatic parsing after extraction | `backlog` | P0 | backend, automation |
| P4-04 | Automatic summarization and podcast generation | `backlog` | P0 | backend, automation |
| P4-05 | Error handling and retry logic | `backlog` | P1 | backend, automation |
| P4-06 | User preferences database table | `backlog` | P1 | backend, database |
| P4-07 | Category priority/ordering preference | `backlog` | P1 | backend |
| P4-08 | Default categories for daily podcast | `backlog` | P1 | backend |
| P4-09 | Voice preference setting | `backlog` | P2 | backend |
| P4-10 | Preferred playback speed setting | `backlog` | P2 | backend |
| P4-11 | Email notification when podcast ready | `backlog` | P2 | backend, notification |
| P4-12 | Settings page in frontend | `backlog` | P1 | frontend |
| P4-13 | New podcast notification indicator | `backlog` | P2 | frontend |
| P4-14 | System status / last run info display | `backlog` | P2 | frontend |
| P4-15 | API usage and cost tracking dashboard | `backlog` | P2 | frontend |

---

# Phase 5: Polish & Advanced Features

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| P5-01 | Bookmark/save newsletters for later | `backlog` | P2 | frontend |
| P5-02 | Search across all parsed content | `backlog` | P1 | backend, frontend |
| P5-03 | Custom category creation | `backlog` | P2 | backend, frontend |
| P5-04 | Weekly/monthly digest options | `backlog` | P2 | backend |
| P5-05 | Cache summaries to avoid re-generation | `backlog` | P1 | backend |
| P5-06 | Batch processing for large volumes | `backlog` | P2 | backend |
| P5-07 | Database indexing and optimization | `backlog` | P2 | backend, database |
| P5-08 | Dark mode | `backlog` | P3 | frontend |
| P5-09 | Mobile-responsive design improvements | `backlog` | P2 | frontend |
| P5-10 | Keyboard shortcuts | `backlog` | P3 | frontend |
| P5-11 | Progressive Web App (PWA) support | `backlog` | P3 | frontend |
| P5-12 | Analytics: listening time tracking | `backlog` | P2 | backend |
| P5-13 | Analytics: completion rates | `backlog` | P2 | backend |
| P5-14 | Analytics dashboard in frontend | `backlog` | P2 | frontend |
| P5-15 | **Parallel AI processing optimization** | `backlog` | P2 | backend, ai, performance |
|       | _Currently processing serially (1 newsletter → next newsletter → category rollup) to respect rate limits. Future: Implement parallel processing with smart batching, rate limit management, and potentially higher-tier API access for faster summarization._ | | | |

---

# Future Ideas (Post-Phase 5)

| ID | Task | Status | Priority | Labels |
|----|------|--------|----------|--------|
| F-01 | **Personalized summaries based on user interests** | `idea` | P1 | ai, personalization |
| F-02 | Track engagement (clicks, time spent) for personalization | `idea` | P2 | personalization |
| F-03 | Thumbs up/down feedback on summaries | `idea` | P1 | personalization, frontend |
| F-04 | Explicit interest settings ("more AI, less fundraising") | `idea` | P2 | personalization |
| F-05 | Learn preferred summary length/detail level | `idea` | P2 | personalization, ai |
| F-06 | Remember read topics to avoid repetition | `idea` | P2 | personalization |
| F-07 | Weight trusted sources more heavily | `idea` | P2 | personalization |
| F-08 | Multi-user support with authentication | `idea` | P1 | backend, auth |
| F-09 | Per-user Gmail connections | `idea` | P1 | backend, gmail |
| F-26 | **"Login with Gmail" user auth & profile** | `idea` | P2 | backend, auth, gmail, frontend |
|       | _Replace the current developer-configured OAuth (credentials.json + token.pickle) with a proper "Login with Gmail" experience. Users should sign up/sign in via Google OAuth in the browser, granting the app Gmail read permission in a single step — no manual credential setup. This creates a user profile tied to their Google account, stores per-user refresh tokens in the DB, and handles token refresh/re-auth transparently. The server-side pickle file approach goes away entirely. Must also include a Privacy Policy and Terms of Service — Google requires these for OAuth consent screen verification, and users should see them linked on the login/sign-up page. Depends on F-08 and F-09._ | | | |
| F-10 | PostgreSQL migration for scalability | `idea` | P2 | backend, database |
| F-11 | Native iOS app | `idea` | P2 | mobile |
| F-12 | Native Android app | `idea` | P2 | mobile |
| F-13 | Offline playback support | `idea` | P2 | mobile |
| F-14 | CarPlay / Android Auto integration | `idea` | P3 | mobile |
| F-15 | Cross-newsletter insights and connections | `idea` | P2 | ai |
| F-16 | Automatic topic trending analysis | `idea` | P2 | ai |
| F-17 | Smart content recommendations | `idea` | P2 | ai |
| F-18 | Spotify/Apple Podcasts distribution | `idea` | P2 | distribution |
| F-19 | RSS feed generation | `idea` | P2 | distribution |
| F-20 | Notion integration for highlights | `idea` | P2 | integration |
| F-21 | Readwise integration | `idea` | P2 | integration |
| F-22 | Support for RSS feeds (not just Gmail) | `idea` | P1 | backend |
| F-23 | YouTube video transcript support | `idea` | P3 | backend |
| F-24 | Twitter/X threads support | `idea` | P3 | backend |
| F-25 | Trello/Notion backlog sync | `idea` | P3 | tooling |

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
| `mobile` | Mobile app features |
| `distribution` | Podcast distribution |
| `integration` | Third-party integrations |
| `tooling` | Development tools |

---

# Quick Stats

**Phase 0:** 5/5 complete (100%)
**Phase 1:** 17/17 complete (100%)
**Phase 2:** 13/18 complete (72%)
**Phase 3:** 0/17 complete (0%)
**Phase 4:** 0/15 complete (0%)
**Phase 5:** 0/14 complete (0%)

**Overall Progress:** 35/86 tasks (41%)

---

# Export Notes

This backlog is formatted for easy import into:
- **Trello**: Copy each phase as a list, tasks as cards
- **Notion**: Import as database with Status, Priority, Labels as properties
- **GitHub Projects**: Create issues from tasks with labels
- **Linear**: Import with priority and status mapping

To generate JSON for programmatic import:
```bash
# Future: Add script to convert this markdown to JSON
python scripts/backlog_to_json.py
```
