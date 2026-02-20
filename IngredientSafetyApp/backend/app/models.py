from sqlalchemy import Column, Integer, String, Boolean, Text, Float
from .database import Base

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    common_names = Column(String(500))
    scores = Column(Text)  # Stored as JSON string
    description = Column(Text)
    concerns = Column(Text) # "Regulation" info can go here or new column
    regulation = Column(String(255))
    is_restricted = Column(Boolean, default=False)
    category = Column(String(50), default="shampoo", index=True)
    target_audience = Column(String(50), default="adult", index=True) # 'adult', 'baby', 'all'
    
    # Quantity Verification
    max_percentage = Column(Float, nullable=True) # e.g. 1.0 for 1%
    regulation_source = Column(String(255), nullable=True) # e.g. "EU Regulation 1223/2009"
    
    # Actionable Alternatives (stored as JSON string)
    alternatives = Column(Text, nullable=True)
    
    # Raw JSON data dump for unmapped fields
    raw_data = Column(Text, nullable=True)
