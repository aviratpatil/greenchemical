from sqlalchemy.orm import Session
from .utils import find_best_match
from .calculator import calculate_safety_score
from .models import Ingredient
from app.classifier import predict_ingredient_safety
from app.recommendations import get_recommendations
import re

def analyze_ingredients_text(text: str, db: Session, category: str = "shampoo", target_audience: str = "adult"):
    # ... (existing parsing logic) ...
    # 1. Parse text
    # Remove common prefixes
    text = re.sub(r'^(Ingredients:|Contains:)\s*', '', text, flags=re.IGNORECASE)
    
    # Remove content inside parentheses (often chemical names or sources) to simplify matching
    text = re.sub(r'\([^)]*\)', '', text)

    # Split by common delimiters (comma, newline, bullet points)
    # Split by common delimiters (comma, newline, bullet points)
    raw_items = [x.strip() for x in re.split(r'[,\n•]+', text) if x.strip()]
    
    analyzed_ingredients = []
    missing_ingredients = []

    for item_text in raw_items:
        # Extract percentage if present (e.g., "Retinol 0.5%")
        # Matches: Name followed by number and %
        # Group 1: Name, Group 2: Percentage
        match_percent = re.search(r'^(.*?)\s+(\d+(\.\d+)?)\s*%$', item_text)
        
        if match_percent:
            clean_name = match_percent.group(1).strip()
            quantity = float(match_percent.group(2))
        else:
            clean_name = item_text
            quantity = None

        # Pass target_audience to find_best_match
        match = find_best_match(clean_name, db, category=category, target_audience=target_audience)
        
        if match:
            # Create a copy or attach the input quantity to the object context for this request
            # We can't modify the DB object directly as it persists
            # So we attach it to a temporary attribute or wrap it
            match.input_quantity = quantity 
            analyzed_ingredients.append(match)
        else:
            # INTEGRATE AI CLASSIFIER HERE
            # 1. Predict safety
            prediction = predict_ingredient_safety(clean_name)
            
            # 2. Save to DB (Learn it for next time)
            # Encode scores to JSON string for storage
            import json
            scores_json = json.dumps({
                "general": prediction['hazard_score'], # Fallback for now
                "carcinogenicity": 0,
                "allergen_potential": 0,
                "endocrine_disruption": 0
            })

            new_ing = Ingredient(
                name=clean_name, # Use original name
                scores=scores_json,
                description=prediction['description'],
                concerns=prediction['concerns'],
                is_restricted=prediction['is_restricted'],
                common_names=clean_name.lower(),
                category=category, # Save with current category
                target_audience=target_audience
            )
            try:
                db.add(new_ing)
                db.commit() # Save learning
                db.refresh(new_ing)
                new_ing.input_quantity = quantity
                analyzed_ingredients.append(new_ing)
            except Exception:
                # Fallback if save fails (e.g. race condition), just use prediction
                db.rollback()
                # Create temp object
                temp_ing = Ingredient(
                    name=clean_name,
                    scores=scores_json,
                    description=prediction['description'],
                    concerns=prediction['concerns'],
                    is_restricted=prediction['is_restricted']
                )
                temp_ing.input_quantity = quantity
                analyzed_ingredients.append(temp_ing)

    # 2. Calculate Score
    result = calculate_safety_score(analyzed_ingredients)
    
    # 3. Format Breakdown for serialization
    breakdown = []
    import json
    for ing in analyzed_ingredients:
        # Decode scores if string
        try:
            scores_dict = json.loads(ing.scores) if isinstance(ing.scores, str) else ing.scores
        except:
            scores_dict = {"general": 5} # Fallback

        # Add quantity warning if verified
        validation_msg = ""
        if hasattr(ing, 'quantity_validation'):
             validation_msg = ing.quantity_validation

        breakdown.append({
            "name": ing.name,
            "scores": scores_dict,
            "description": ing.description,
            "is_restricted": getattr(ing, "is_restricted", False),
            "regulation": getattr(ing, "regulation", ""),
            "input_quantity": getattr(ing, "input_quantity", None),
            "quantity_validation": validation_msg,
            "max_percentage": getattr(ing, "max_percentage", None)
        })

    # 4. Get Recommendations
    # Pass flattened format if needed by existing recommendation logic, or update it
    # For now, simplistic adaptation
    recs = get_recommendations(breakdown)

    result["ingredients_breakdown"] = breakdown
    result["missing_ingredients"] = missing_ingredients
    result["recommendations"] = recs
    
    return result
