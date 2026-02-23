"""
Database models for Newsletter Podcast Agent
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()
DEFAULT_OWNER_EMAIL = "default@local"


class Newsletter(Base):
    """Newsletter model - stores parsed newsletter data"""
    __tablename__ = 'newsletters'
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True, nullable=False)
    owner_email = Column(String, index=True, nullable=False, default=DEFAULT_OWNER_EMAIL)
    sender_name = Column(String, index=True)
    sender_email = Column(String, index=True)
    subject = Column(String)
    date = Column(String)  # Original email date string
    received_at = Column(DateTime, default=datetime.utcnow)
    
    # Categorization
    platform = Column(String, index=True)  # substack, beehiiv, tldr, etc.
    category = Column(String, index=True)  # product_ai, health_fitness, etc.
    
    # Content
    raw_html = Column(Text)  # Original HTML content
    parsed_content = Column(Text)  # Clean parsed text
    title = Column(String)
    sections = Column(Text)  # JSON string of sections
    links = Column(Text)  # JSON string of links
    images = Column(Text)  # JSON string of image URLs
    
    # Metadata
    extra_metadata = Column(Text)  # JSON string for additional metadata
    parsing_success = Column(Boolean, default=True)
    needs_review = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        import json
        return {
            'id': self.id,
            'message_id': self.message_id,
            'owner_email': self.owner_email,
            'sender_name': self.sender_name,
            'sender_email': self.sender_email,
            'subject': self.subject,
            'date': self.date,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'platform': self.platform,
            'category': self.category,
            'parsed_content': self.parsed_content,
            'title': self.title,
            'sections': json.loads(self.sections) if self.sections else [],
            'links': json.loads(self.links) if self.links else [],
            'images': json.loads(self.images) if self.images else [],
            'metadata': json.loads(self.extra_metadata) if self.extra_metadata else {},
            'parsing_success': self.parsing_success,
            'needs_review': self.needs_review,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./newsletters.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if 'sqlite' in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    _ensure_owner_email_column()


def _ensure_owner_email_column():
    """
    Backward-compatible schema patching for existing deployments.
    """
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("newsletters")}
    with engine.begin() as conn:
        if "owner_email" not in columns:
            conn.execute(text("ALTER TABLE newsletters ADD COLUMN owner_email VARCHAR"))
        conn.execute(
            text(
                "UPDATE newsletters SET owner_email = :owner WHERE owner_email IS NULL OR owner_email = ''"
            ),
            {"owner": DEFAULT_OWNER_EMAIL},
        )
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_newsletters_owner_email ON newsletters (owner_email)"))
