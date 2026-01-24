# Development Guide

Quick reference for developing the Newsletter Podcast Agent.

## 🚀 Quick Start

```bash
# First time setup
./setup.sh

# Start both servers
./start.sh

# Or start individually:
# Backend: cd backend && source venv/bin/activate && python main.py
# Frontend: cd frontend && npm run dev
```

## 📂 Code Organization

### Backend Structure

```
backend/
├── main.py                 # FastAPI app, routes, startup
├── database.py             # SQLAlchemy models, DB setup
├── newsletter_service.py   # Business logic (Gmail, parsing)
└── requirements.txt        # Python dependencies
```

### Frontend Structure

```
frontend/src/
├── main.jsx               # React entry point
├── App.jsx                # Main app with routing
├── api.js                 # Backend API client
└── components/
    ├── Header.jsx         # Top bar with extract button
    ├── FilterBar.jsx      # Category/date filters
    ├── NewsletterList.jsx # Main list view
    └── NewsletterDetail.jsx # Detail view
```

## 🔧 Making Changes

### Adding a New API Endpoint

1. Add route in `backend/main.py`:
```python
@app.get("/api/my-endpoint")
def my_endpoint(db: Session = Depends(get_db)):
    # Your logic here
    return {"data": "result"}
```

2. Add to `frontend/src/api.js`:
```javascript
export const newsletterApi = {
  // ... existing methods
  
  myEndpoint: async () => {
    const response = await api.get('/api/my-endpoint');
    return response.data;
  },
};
```

3. Use in components:
```javascript
import { newsletterApi } from '../api';

const data = await newsletterApi.myEndpoint();
```

### Adding a New Newsletter Platform

1. Add parser class in `parsers/newsletter_parser.py`:
```python
class MyPlatformParser:
    def parse(self, html_content: str) -> Dict:
        # Parse logic
        return {
            'content': '...',
            'title': '...',
            # ...
        }
```

2. Add detection in `NewsletterParser._detect_platform()`:
```python
if 'myplatform.com' in email_lower:
    return 'myplatform'
```

3. Add to routing in `_route_to_parser()`:
```python
parsers = {
    # ... existing parsers
    'myplatform': self.myplatform_parser,
}
```

### Adding a New Category

1. Update mapping in `parsers/newsletter_parser.py`:
```python
CATEGORY_MAPPING = {
    # ... existing mappings
    'new newsletter': 'my_category',
}
```

2. Update category labels in components:
```javascript
const getCategoryLabel = (category) => {
  const labels = {
    // ... existing labels
    'my_category': 'My Category',
  };
  return labels[category] || category;
};
```

3. Add category color:
```javascript
const getCategoryColor = (category) => {
  const colors = {
    // ... existing colors
    'my_category': '#ff5733',
  };
  return colors[category] || '#95a5a6';
};
```

## 🔍 Debugging

### Backend Debugging

```bash
# Check backend is running
curl http://localhost:8000

# View API docs
open http://localhost:8000/docs

# Check database
cd backend
sqlite3 newsletters.db
> .tables
> SELECT * FROM newsletters LIMIT 5;
```

### Frontend Debugging

```bash
# Check frontend dev server
open http://localhost:5173

# View console in browser DevTools (F12)
# Check Network tab for API calls
```

### Common Issues

**Backend returns 404 for all routes:**
- Check CORS settings in main.py
- Verify backend is running on port 8000

**Frontend can't reach backend:**
- Check proxy settings in vite.config.js
- Verify both servers are running

**Parsing fails silently:**
- Check backend console for errors
- Add logging in newsletter_service.py
- Verify HTML structure matches parser expectations

## 📊 Database Queries

```bash
cd backend
sqlite3 newsletters.db
```

Useful queries:

```sql
-- Count newsletters by category
SELECT category, COUNT(*) 
FROM newsletters 
GROUP BY category;

-- Find newsletters needing review
SELECT sender_name, subject 
FROM newsletters 
WHERE needs_review = 1;

-- Recent newsletters
SELECT sender_name, subject, date 
FROM newsletters 
ORDER BY received_at DESC 
LIMIT 10;

-- Check parsing success rate
SELECT 
  parsing_success,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM newsletters), 2) as percentage
FROM newsletters 
GROUP BY parsing_success;
```

## 🧪 Testing

### Test Newsletter Extraction

```bash
cd backend
source venv/bin/activate
python

>>> from newsletter_service import NewsletterService
>>> from database import SessionLocal
>>> service = NewsletterService()
>>> service.authenticate_gmail()
>>> db = SessionLocal()
>>> stats = service.extract_newsletters(db, days_back=1)
>>> print(stats)
```

### Test Parser

```bash
cd parsers
python

>>> from newsletter_parser import NewsletterParser
>>> parser = NewsletterParser()
>>> # Create a sample Gmail message structure
>>> # Then: result = parser.parse_gmail_message(msg)
```

## 📝 Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints where helpful
- Document functions with docstrings
- Use meaningful variable names

### JavaScript (Frontend)
- Use modern ES6+ features
- Prefer functional components with hooks
- Keep components focused (single responsibility)
- Use meaningful component and variable names

## 🔄 Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
git add .
git commit -m "Add: description of changes"

# Push to remote
git push origin feature/my-feature

# Create pull request (if working with team)
```

## 📦 Deployment Considerations (Future)

For future production deployment:

1. **Environment Variables:**
   - Create `.env` file for secrets
   - Never commit credentials.json or .env

2. **Database:**
   - Migrate from SQLite to PostgreSQL
   - Set up proper backups

3. **Security:**
   - Use HTTPS
   - Implement rate limiting
   - Add authentication

4. **Hosting:**
   - Backend: Railway, Render, or AWS
   - Frontend: Vercel, Netlify, or Cloudflare Pages
   - Consider using Docker

## 📚 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Gmail API Python](https://developers.google.com/gmail/api/quickstart/python)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Vite Docs](https://vitejs.dev/)

## 🎯 Next Phase Preview (Phase 2)

Phase 2 will add:
- Claude API integration for summarization
- Summary viewing in UI
- Script generation for podcasts

Key files to prepare:
- `backend/summarization_service.py` - Claude API integration
- `frontend/src/components/SummaryView.jsx` - Summary display
- Database schema updates for storing summaries
