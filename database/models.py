from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from database.database import Base


class FeedbackORM(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    first_name = Column(String)
    message = Column(Text)
    admin_response = Column(Text, nullable=True)
    is_answered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
