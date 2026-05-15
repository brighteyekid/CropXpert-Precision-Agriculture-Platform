"""Government scheme ORM model."""
from sqlalchemy import Column, Integer, String, Text, Date
from core.database import Base


class GovernmentScheme(Base):
    __tablename__ = "government_schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    benefit_amount = Column(String(100))
    eligibility = Column(Text)
    documents_required = Column(Text)
    apply_url = Column(String(500))
    scheme_type = Column(String(20))  # 'welfare' or 'loan'
    applicable_states = Column(Text)  # JSON string: ["all"] or ["Maharashtra","UP"]
    last_updated = Column(Date)
