import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from shared.infrastructure.database.base import Base

class VisitorRequest(Base):
    __tablename__ = "visitor_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference = Column(String(20), nullable=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    cin = Column(String(20), nullable=True)
    campus = Column(String(50), nullable=True)
    intent = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
