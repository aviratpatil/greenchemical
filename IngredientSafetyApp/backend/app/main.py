from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict

from .database import SessionLocal
from .services import analyze_ingredients_text
from .routers import admin

app = FastAPI()

app.include_router(admin.router)

# Input Model
class AnalyzeRequest(BaseModel):
    text: str
    category: str = "shampoo" # Default to shampoo
    target_audience: str = "adult" # 'adult', 'baby', 'all'

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CORS Setup
origins = [
    "http://localhost:5173",
    "http://localhost:5174", # Added current user port
    "*", # Allow all for dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Ingredient Safety API is running"}

@app.post("/analyze")
def analyze_ingredients(request: AnalyzeRequest, db: Session = Depends(get_db)):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        results = analyze_ingredients_text(
            request.text, 
            db, 
            category=request.category,
            target_audience=request.target_audience
        )
        return results
    except Exception as e:
        # In a real app, log this
        print(f"Error analyzing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class IngredientRequest(BaseModel):
    ingredient: str
    category: str = "shampoo"
    target_audience: str = "adult"
    quantity: float | None = None

@app.post("/analyze/details")
def analyze_details(request: IngredientRequest):
    from app.gemini_service import get_ingredient_details
    details = get_ingredient_details(
        request.ingredient, 
        request.category, 
        request.target_audience, 
        request.quantity
    )
    return {"details": details}


# ── Formulation-level expert analysis ──────────────────────────────────────

class FormulationRequest(BaseModel):
    ingredient_list: List[str]               # ordered INCI list
    product_type: str = "shampoo"            # e.g. "shampoo", "face cream"
    region: str = "EU"                       # "EU", "US", "both"
    target_group: str = "general adult"      # e.g. "general adult", "children under 3"
    known_concentrations: Optional[Dict[str, float]] = None  # {"phenoxyethanol": 0.8}

@app.post("/analyze/formulation")
def analyze_formulation(request: FormulationRequest):
    """
    Full formulation-level cosmetic safety analysis.
    Returns overall_verdict, per-ingredient breakdown, combination alerts,
    and regulatory flags based on the expert system prompt framework.
    """
    if not request.ingredient_list:
        raise HTTPException(status_code=400, detail="ingredient_list cannot be empty.")

    from app.formulation_analyzer import analyze_formulation as _analyze
    try:
        result = _analyze(
            ingredient_list=request.ingredient_list,
            product_type=request.product_type,
            region=request.region,
            target_group=request.target_group,
            known_concentrations=request.known_concentrations or {},
        )
        return result
    except Exception as e:
        print(f"Formulation analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
