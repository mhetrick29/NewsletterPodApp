# Getting Started with Newsletter Podcast Agent (Phase 1)

## What You've Got

I've built you a complete Phase 1 web application with:

✅ **FastAPI Backend** - Extracts and parses newsletters from Gmail  
✅ **React Frontend** - Beautiful web interface to view and filter newsletters  
✅ **Multi-Platform Support** - Handles Substack, Beehiiv, TLDR, ConvertKit, and more  
✅ **Automatic Categorization** - Sorts into Product & AI, Health & Fitness, Finance, Sahil Bloom  
✅ **SQLite Database** - Stores all parsed newsletters  

## Quick Start (5 minutes)

### Step 1: Get Google OAuth Credentials

You need a `credentials.json` file to connect to Gmail:

1. Go to https://console.cloud.google.com/
2. Create a new project (or select your existing one)
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (choose "Desktop app")
5. Download the credentials file
6. Save it as `credentials.json` in the `parsers/` directory

**You already have one in the project files, but it's from your previous setup. If it doesn't work, create a new one.**

### Step 2: Label Your Newsletters in Gmail

1. Go to Gmail
2. Create a label called "newsletters" (exactly that, lowercase)
3. Apply it to some of your newsletter emails
4. (Optional) Set up a filter to auto-label incoming newsletters

### Step 3: Run Setup

Open a terminal in the `newsletter-podcast-agent` directory:

```bash
./setup.sh
```

This installs all dependencies for both backend and frontend.

### Step 4: Start the Application

```bash
./start.sh
```

This starts both servers:
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173

### Step 5: Extract Your Newsletters

1. Open http://localhost:5173 in your browser
2. Click the **"Extract Newsletters"** button
3. First time: You'll be prompted to authorize via Google OAuth
4. After authorization, your newsletters will be extracted and displayed!

## What You Can Do Now

### View Newsletters
- See all your extracted newsletters in a beautiful card grid
- Click any newsletter to view full content
- View sections, links, and metadata

### Filter Newsletters
- Filter by category (Product & AI, Health & Fitness, Finance, Sahil Bloom)
- Filter by date range
- Clear filters anytime

### Extract More Newsletters
- Click "Extract Newsletters" anytime to fetch new ones
- By default it gets newsletters from the last 24 hours
- Already-extracted newsletters won't be duplicated

## Project Structure

```
newsletter-podcast-agent/
├── README.md              # Full documentation
├── DEVELOPMENT.md         # Developer guide
├── setup.sh              # One-time setup script
├── start.sh              # Start both servers
│
├── backend/              # FastAPI backend
│   ├── main.py          # API routes
│   ├── database.py      # Database models
│   ├── newsletter_service.py  # Business logic
│   └── requirements.txt
│
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── App.jsx     # Main app
│   │   └── api.js      # Backend API client
│   └── package.json
│
└── parsers/             # Newsletter parsing
    ├── newsletter_parser.py
    ├── gmail_newsletter_extractor.py
    └── credentials.json  # Your Google OAuth credentials
```

## API Endpoints You Can Use

The backend exposes these endpoints (see http://localhost:8000/docs for interactive docs):

- `GET /api/newsletters` - List newsletters with filtering
- `GET /api/newsletters/{id}` - Get newsletter details
- `POST /api/extract` - Trigger manual extraction
- `GET /api/categories` - Get category breakdown
- `GET /api/stats` - Get overall statistics

## Common Issues & Solutions

### "credentials.json not found"
➡️ Make sure you've placed your Google OAuth credentials in `parsers/credentials.json`

### "No newsletters found"
➡️ Make sure you have emails labeled "newsletters" in Gmail

### Backend won't start
➡️ Make sure you've run `./setup.sh` first  
➡️ Check Python 3.8+ is installed: `python3 --version`

### Frontend won't start
➡️ Make sure you've run `./setup.sh` first  
➡️ Check Node.js is installed: `node --version`

### CORS errors in browser
➡️ Make sure both backend (8000) and frontend (5173) are running  
➡️ Check the URLs in your browser console

## What's Next (Your Roadmap)

You've completed **Phase 1**! Here's what comes next:

### Phase 2: AI Summarization (Next)
- Integrate Claude API to summarize newsletters
- Generate podcast scripts
- View summaries in the UI

### Phase 3: Audio Generation
- Text-to-speech integration
- Audio player in the UI
- Download podcasts

### Phase 4: Automation
- Daily automated extraction
- Scheduled podcast generation
- Notifications

### Phase 5: Polish
- Search across newsletters
- Bookmark favorites
- Advanced features

## Need Help?

1. Check `README.md` for full documentation
2. Check `DEVELOPMENT.md` for development tips
3. Look at the code comments
4. Check browser console (F12) for frontend errors
5. Check terminal output for backend errors

## Tips for Success

1. **Start Small**: Extract just a few newsletters first to test
2. **Check Parsing**: Some newsletters might need manual review - they'll be flagged
3. **Iterate**: If a newsletter parses poorly, you can improve the parser
4. **Use Categories**: The filtering makes it easy to focus on specific topics

## Your Newsletter Inventory

Based on your `newsletter_sources.json`, you have **45 newsletters** including:

**Product & AI (23)**:
- Peter Yang, Lenny's Newsletter, Ben Thompson (Stratechery)
- TLDR, TLDR AI, TLDR Product
- Half Baked, The Code by Superhuman
- Elena's Growth Scoop, Aakash Gupta, and many more

**Health & Fitness (1)**:
- mario fraioli (The Morning Shakeout)

**Finance (2)**:
- Snacks, Chartr

**Sahil Bloom (1)**:
- Curiosity Chronicle

All of these will be automatically categorized when extracted!

## Enjoy!

You now have a working newsletter viewer. Next, we'll add AI summarization and podcast generation. For now, enjoy browsing your newsletters in a clean, organized interface! 🎉
