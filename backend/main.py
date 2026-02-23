"""
FastAPI application for Newsletter Podcast Agent
Simplified: fetch emails by date, generate PDF summary
"""
from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import io
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from database import get_db, init_db, Newsletter
from newsletter_service import NewsletterService, normalize_owner_email

app = FastAPI(
    title="Newsletter Podcast Agent API",
    description="Fetch daily newsletters and generate PDF summaries",
    version="2.0.0"
)

default_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
configured_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[*default_origins, *configured_origins],
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized")
    # Clean up newsletters older than 10 days
    from database import SessionLocal
    db = SessionLocal()
    try:
        NewsletterService.cleanup_old_newsletters(db)
    except Exception as e:
        logger.warning(f"Startup cleanup failed: {e}")
    finally:
        db.close()


# ---------- Request / Response models ----------

class ExtractionRequest(BaseModel):
    target_date: Optional[str] = None  # YYYY-MM-DD; defaults to today
    max_results: int = 100
    user_email: Optional[str] = None


# ---------- Endpoints ----------

@app.get("/")
def root():
    """Health check"""
    return {"status": "running", "version": "2.0.0"}


@app.get("/api/newsletters")
def list_newsletters(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    user_email: Optional[str] = Query(None, description="User identity for multi-user isolation"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    db: Session = Depends(get_db)
):
    """Get newsletters for a specific date."""
    owner_email = normalize_owner_email(user_email or x_user_email)
    target_date, start_dt, end_dt = _get_date_boundaries(date)

    newsletters = db.query(Newsletter).filter(
        Newsletter.owner_email == owner_email,
        Newsletter.received_at >= start_dt,
        Newsletter.received_at <= end_dt
    ).order_by(Newsletter.received_at.desc()).all()

    return {
        "user_email": owner_email,
        "date": target_date.isoformat(),
        "total": len(newsletters),
        "newsletters": [
            {
                "id": nl.id,
                "sender_name": nl.sender_name,
                "subject": nl.subject,
                "date": nl.date,
            }
            for nl in newsletters
        ]
    }


@app.post("/api/extract")
def extract_newsletters(
    request: ExtractionRequest,
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    db: Session = Depends(get_db)
):
    """Fetch newsletters from Gmail for a target date."""
    owner_email = normalize_owner_email(request.user_email or x_user_email)
    service = NewsletterService()

    try:
        service.authenticate_gmail()

        stats = service.extract_newsletters(
            db=db,
            target_date=request.target_date,
            max_results=request.max_results,
            owner_email=owner_email,
        )

        return {
            "success": True,
            "user_email": owner_email,
            "message": f"Extracted {stats['newly_parsed']} new newsletters",
            "stats": stats
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.get("/api/summary-pdf")
def get_summary_pdf(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    user_email: Optional[str] = Query(None, description="User identity for multi-user isolation"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    db: Session = Depends(get_db)
):
    """Generate and return a PDF summary for a given date."""
    owner_email = normalize_owner_email(user_email or x_user_email)
    import time
    from fastapi.responses import StreamingResponse
    from pdf_service import generate_summary_pdf

    target_date, start_dt, end_dt = _get_date_boundaries(date)
    logger.info(f"PDF summary: {start_dt} to {end_dt} UTC (local: {target_date})")

    newsletters = db.query(Newsletter).filter(
        Newsletter.owner_email == owner_email,
        Newsletter.received_at >= start_dt,
        Newsletter.received_at <= end_dt
    ).order_by(Newsletter.received_at.desc()).all()

    if not newsletters:
        raise HTTPException(status_code=404, detail=f"No newsletters found for {target_date.isoformat()}")

    from summarization_service import SummarizationService
    try:
        service = SummarizationService()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))

    summaries = []
    for idx, nl in enumerate(newsletters):
        if not nl.raw_html:
            logger.warning(f"Newsletter {nl.id} has no HTML content, skipping")
            continue

        try:
            logger.info(f"[PDF] Summarizing: {nl.sender_name} - {nl.subject}")
            nl_summary = service.summarize_newsletter(nl.raw_html, nl.sender_name, nl.subject)
            nl_summary['id'] = nl.id
            nl_summary['sender_name'] = nl.sender_name
            summaries.append(nl_summary)

            if idx < len(newsletters) - 1:
                time.sleep(5)
        except Exception as e:
            logger.error(f"[PDF] Failed to summarize newsletter {nl.id}: {e}")
            summaries.append({
                'id': nl.id,
                'sender_name': nl.sender_name,
                'title': nl.subject,
                'summary': 'Failed to generate summary',
                'key_points': [],
            })

    themes = {}
    if len(summaries) >= 2:
        try:
            logger.info("[PDF] Synthesizing themes across newsletters")
            time.sleep(5)
            themes = service.synthesize_themes(summaries)
        except Exception as e:
            logger.error(f"[PDF] Theme synthesis failed: {e}")
            themes = {"themes": [], "synthesis": ""}

    pdf_bytes = generate_summary_pdf(target_date.isoformat(), summaries, themes)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="newsletter-summary-{target_date.isoformat()}.pdf"'
        }
    )


# ---------- Helpers ----------

def _get_date_boundaries(date_str: str = None):
    """Resolve a date string (or today) into UTC start/end boundaries."""
    from zoneinfo import ZoneInfo

    local_tz = ZoneInfo('America/Los_Angeles')
    try:
        import subprocess
        tz_result = subprocess.run(['readlink', '/etc/localtime'], capture_output=True, text=True, timeout=1)
        if tz_result.returncode == 0:
            tz_path = tz_result.stdout.strip()
            if 'zoneinfo' in tz_path:
                tz_name = tz_path.split('zoneinfo/')[-1]
                local_tz = ZoneInfo(tz_name)
    except Exception as e:
        logger.warning(f"Could not detect timezone, using America/Los_Angeles: {e}")

    if date_str:
        target_date = datetime.fromisoformat(date_str).date()
    else:
        target_date = datetime.now(local_tz).date()

    local_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=local_tz)
    local_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=local_tz)

    start_dt = local_start.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    end_dt = local_end.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)

    return target_date, start_dt, end_dt


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
