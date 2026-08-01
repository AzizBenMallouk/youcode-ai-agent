import datetime
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from shared.infrastructure.database.base import Base

class NewsletterSubscription(Base):
    __tablename__ = "newsletter_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference = Column(String(20), nullable=True, index=True)
    phone = Column(String(50), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    full_name = Column(String(100), nullable=True)
    motif = Column(String(100), nullable=True)
    campus = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
