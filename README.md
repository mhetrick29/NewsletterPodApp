# Newsletter Podcast Agent - Phase 1

AI-powered newsletter extraction and viewing system. This Phase 1 implementation provides a web interface to extract, parse, and view newsletters from Gmail.

## 🎯 What's Included (Phase 1)

- **Backend (FastAPI):**
  - Newsletter extraction from Gmail API
  - Multi-platform parsing (Substack, Beehiiv, TLDR, ConvertKit)
  - SQLite database storage
  - REST API endpoints
  - Automatic categorization

- **Frontend (React + Vite):**
  - Newsletter list view with cards
  - Detailed newsletter viewer
  - Category filtering (Product & AI, Health & Fitness, Finance, Sahil Bloom)
  - Date range filtering
  - Manual extraction trigger
  - Responsive design

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **Gmail account** with newsletters labeled "newsletters"
- **Google Cloud credentials** (credentials.json)

## 🚀 Quick Start

### 1. Google Cloud Setup

First, you need to create OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the **Gmail API**
4. Create **OAuth 2.0 credentials** (Desktop app)
5. Download credentials and save as `credentials.json` in the `parsers/` directory

### 2. Gmail Setup

1. In Gmail, create a label called **"newsletters"**
2. Apply this label to your newsletter emails
3. You can set up filters to auto-label incoming newsletters

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy credentials to parsers directory (if not already there)
# Make sure credentials.json is in ../parsers/

# Start the backend server
python main.py
```

The backend will start at `http://localhost:8000`

### 4. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start at `http://localhost:5173`

### 5. First Run

1. Open http://localhost:5173 in your browser
2. Click **"Extract Newsletters"** button
3. First time: You'll be redirected to Google OAuth
4. Authorize the app to read your Gmail
5. Newsletters will be extracted and displayed

## 📁 Project Structure

```
newsletter-podcast-agent/
├── backend/
│   ├── main.py                  # FastAPI application
│   ├── database.py              # SQLAlchemy models
│   ├── newsletter_service.py    # Business logic
│   ├── requirements.txt         # Python dependencies
│   └── newsletters.db           # SQLite database (created automatically)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx       # Top header with extract button
│   │   │   ├── FilterBar.jsx    # Category/date filters
│   │   │   ├── NewsletterList.jsx    # Main list view
│   │   │   └── NewsletterDetail.jsx  # Detail view
│   │   ├── App.jsx              # Main app component
│   │   ├── api.js               # Backend API client
│   │   └── main.jsx             # React entry point
│   ├── package.json
│   └── vite.config.js
│
└── parsers/
    ├── newsletter_parser.py     # Multi-platform parser
    ├── gmail_newsletter_extractor.py
    ├── credentials.json         # Google OAuth credentials
    └── token.pickle            # Auth token (created after first auth)
```

## 🔧 API Endpoints

### GET /api/newsletters
Get list of newsletters with optional filtering
- Query params: `category`, `start_date`, `end_date`, `limit`, `offset`

### GET /api/newsletters/{id}
Get detailed newsletter information

### POST /api/extract
Manually trigger newsletter extraction from Gmail
- Body: `{ "days_back": 1, "max_results": 100 }`

### GET /api/categories
Get all categories with counts

### GET /api/stats
Get overall statistics

## 📊 Categories

Newsletters are automatically categorized:

- **Product & AI**: Peter Yang, Lenny, Stratechery, TLDR, Half Baked, etc.
- **Health & Fitness**: The Morning Shakeout, FittInsider (Anthony Vennare), Sweat Science
- **Finance**: Snacks, Chartr
- **Sahil Bloom**: Curiosity Chronicle (dedicated category)

## 🎨 Features

### Current (Phase 1)
- ✅ Gmail extraction with OAuth
- ✅ Multi-platform parsing (5 platforms)
- ✅ Automatic categorization
- ✅ Web interface with list and detail views
- ✅ Category and date filtering
- ✅ Manual extraction trigger
- ✅ Responsive design

### Coming in Phase 2
- 🔜 AI summarization with Claude API
- 🔜 Podcast script generation
- 🔜 Summary viewing in UI

### Coming in Phase 3
- 🔜 Text-to-speech audio generation
- 🔜 Audio player
- 🔜 Download podcasts

## 🐛 Troubleshooting

### "credentials.json not found"
Make sure you've downloaded OAuth credentials from Google Cloud Console and placed them in the `parsers/` directory.

### "No newsletters found"
1. Verify you have emails with the "newsletters" label in Gmail
2. Try extracting newsletters for more days: modify the extraction request
3. Check backend logs for parsing errors

### Backend won't start
1. Make sure virtual environment is activated
2. Check all dependencies are installed: `pip install -r requirements.txt`
3. Verify Python version is 3.8+

### Frontend won't start
1. Make sure Node.js is installed: `node --version`
2. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
3. Check port 5173 is not in use

### CORS errors
Make sure both backend (port 8000) and frontend (port 5173) are running. The backend has CORS configured for localhost:5173.

## 📝 Next Steps

After Phase 1 is working:

1. **Phase 2**: Add Claude API integration for summarization
2. **Phase 3**: Add text-to-speech for podcast generation
3. **Phase 4**: Add automation and scheduling
4. **Phase 5**: Polish and advanced features

## 🔐 Security Notes

- `credentials.json` and `token.pickle` contain sensitive auth data
- Never commit these files to version control
- The app only requests read-only Gmail access
- No newsletter content is shared with third parties (except AI providers in later phases)

## 📄 License

Part of the Newsletter Podcast Agent project.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!
