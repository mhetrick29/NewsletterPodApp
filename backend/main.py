"""
FastAPI application for Newsletter Podcast Agent
Phase 1: Core backend with newsletter extraction and viewing
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from database import get_db, init_db, Newsletter
from newsletter_service import NewsletterService

# Initialize FastAPI app
app = FastAPI(
    title="Newsletter Podcast Agent API",
    description="Backend API for newsletter extraction, parsing, and podcast generation",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Database initialized")


# Pydantic models for request/response
class ExtractionRequest(BaseModel):
    days_back: int = 1
    max_results: int = 100


class NewsletterListResponse(BaseModel):
    id: int
    sender_name: str
    subject: str
    category: str
    date: str
    platform: str
    needs_review: bool
    
    class Config:
        from_attributes = True


# API Endpoints

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Newsletter Podcast Agent API",
        "version": "1.0.0"
    }


@app.get("/api/newsletters", response_model=List[dict])
def list_newsletters(
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get list of newsletters with optional filtering
    
    Query Parameters:
    - category: Filter by category (product_ai, health_fitness, finance, sahil_bloom)
    - start_date: Filter newsletters received after this date
    - end_date: Filter newsletters received before this date
    - limit: Maximum number of results (default: 100, max: 500)
    - offset: Pagination offset (default: 0)
    """
    service = NewsletterService()
    
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    newsletters = service.get_newsletters(
        db=db,
        category=category,
        start_date=start_dt,
        end_date=end_dt,
        limit=limit,
        offset=offset
    )
    
    return [nl.to_dict() for nl in newsletters]


@app.get("/api/newsletters/{newsletter_id}")
def get_newsletter(newsletter_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific newsletter
    
    Path Parameters:
    - newsletter_id: Database ID of the newsletter
    """
    service = NewsletterService()
    newsletter = service.get_newsletter_by_id(db, newsletter_id)
    
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    
    return newsletter.to_dict()


@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Get all newsletter categories with counts
    
    Returns list of categories and how many newsletters are in each
    """
    service = NewsletterService()
    return service.get_categories(db)


@app.post("/api/extract")
def extract_newsletters(
    request: ExtractionRequest,
    db: Session = Depends(get_db)
):
    """
    Manually trigger newsletter extraction from Gmail
    
    Request Body:
    - days_back: How many days back to search (default: 1)
    - max_results: Maximum number of emails to retrieve (default: 100)
    
    Returns statistics about the extraction
    """
    service = NewsletterService()
    
    try:
        # Authenticate with Gmail
        service.authenticate_gmail()
        
        # Extract and parse newsletters
        stats = service.extract_newsletters(
            db=db,
            days_back=request.days_back,
            max_results=request.max_results
        )
        
        return {
            "success": True,
            "message": f"Extracted {stats['newly_parsed']} new newsletters",
            "stats": stats
        }
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Get overall statistics about the newsletter database
    
    Returns:
    - Total number of newsletters
    - Breakdown by category
    - Breakdown by platform
    - Recent activity
    """
    from sqlalchemy import func
    
    # Total count
    total = db.query(func.count(Newsletter.id)).scalar()
    
    # By category
    by_category = db.query(
        Newsletter.category,
        func.count(Newsletter.id).label('count')
    ).group_by(Newsletter.category).all()
    
    # By platform
    by_platform = db.query(
        Newsletter.platform,
        func.count(Newsletter.id).label('count')
    ).group_by(Newsletter.platform).all()
    
    # Needs review count
    needs_review = db.query(func.count(Newsletter.id)).filter(
        Newsletter.needs_review == True
    ).scalar()
    
    # Recent newsletters (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent = db.query(func.count(Newsletter.id)).filter(
        Newsletter.received_at >= seven_days_ago
    ).scalar()
    
    return {
        "total_newsletters": total,
        "needs_review": needs_review,
        "recent_7_days": recent,
        "by_category": [{"category": r.category, "count": r.count} for r in by_category],
        "by_platform": [{"platform": r.platform, "count": r.count} for r in by_platform]
    }


from datetime import timedelta

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
