from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict
from app.database import SessionLocal
from app.models import Ingredient

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Returns general statistics about the database.
    """
    total_ingredients = db.query(Ingredient).count()
    shampoo_count = db.query(Ingredient).filter(Ingredient.category == 'shampoo').count()
    toothpaste_count = db.query(Ingredient).filter(Ingredient.category == 'toothpaste').count()
    hazardous_count = db.query(Ingredient).filter(Ingredient.hazard_score >= 7).count()

    return {
        "total_ingredients": total_ingredients,
        "shampoo_count": shampoo_count,
        "toothpaste_count": toothpaste_count,
        "hazardous_count": hazardous_count
    }

@router.get("/popular")
def get_popular_ingredients(db: Session = Depends(get_db)):
    """
    Returns the top 10 most common ingredients (simulated by querying all for now).
    In a real app, you would have a 'scan_count' on the Ingredient model.
    For this project, we'll return the top 10 most hazardous ones as 'High Priority'.
    """
    # Just returning top 15 hazardous for now to populate the chart
    top_hazardous = db.query(Ingredient).filter(Ingredient.hazard_score >= 7)\
        .order_by(desc(Ingredient.hazard_score))\
        .limit(10).all()
        
    return [
        {"name": i.name, "score": i.hazard_score, "category": i.category} 
        for i in top_hazardous
    ]

@router.get("/recent")
def get_recent_ingredients(db: Session = Depends(get_db)):
    """
    Returns the last 20 added ingredients (simulated by ID desc).
    """
    recent = db.query(Ingredient).order_by(desc(Ingredient.id)).limit(20).all()
    
    return [
        {"id": i.id, "name": i.name, "score": i.hazard_score, "category": i.category, "is_restricted": i.is_restricted}
        for i in recent
    ]
