from sqlalchemy.orm import Session
from .models import Ingredient
import difflib

def find_best_match(raw_name: str, db: Session, category: str = "shampoo", target_audience: str = "adult"):
    """
    Finds the best matching ingredient in the database using fuzzy search.
    Returns the Ingredient object or None if no close match is found.
    """
    # Normalize input
    cleaned_name = raw_name.strip().lower()
    
    # 1. Exact match attempt
    # Filter by category and target audience (or 'all')
    query = db.query(Ingredient).filter(
        Ingredient.name.ilike(cleaned_name),
        Ingredient.category.in_([category, "both"]),
        Ingredient.target_audience.in_([target_audience, "all"])
    ).first()
    
    if query:
        return query

    # 2. Fuzzy match
    # Fetch all names in this category/audience
    all_ingredients = db.query(Ingredient).filter(
        Ingredient.category.in_([category, "both"]),
        Ingredient.target_audience.in_([target_audience, "all"])
    ).all()
    
    # Create a map of lower_name -> ingredient
    name_map = {ing.name.lower(): ing for ing in all_ingredients}
    
    matches = difflib.get_close_matches(cleaned_name, name_map.keys(), n=1, cutoff=0.7)
    
    if matches:
        return name_map[matches[0]]
        
    return None
