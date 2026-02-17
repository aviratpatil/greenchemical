def calculate_safety_score(ingredients_list):
    """
    Calculates safety score based on Rank-Weighted Hazard Index.
    ingredients_list: List of objects (Ingredient models or dicts) with attributes:
                      - hazard_score (int)
                      - is_restricted (bool)
                      - name (str)
    """
    if not ingredients_list:
        return {
            "score": 0,
            "risk_level": "Unknown",
            "key_concerns": ["No ingredients provided"]
        }

    total_weighted_hazard = 0
    max_possible_weighted_hazard = 0
    has_restricted = False
    key_concerns = []

    for i,ing in enumerate(ingredients_list):
        # Determine Weight (Position based)
        if i < 5:
            weight = 3.0
        elif i < 10:
            weight = 2.0
        else:
            weight = 1.0

        # Extract score from JSON or fallback
        # ing.scores might be a dict (if we pre-processed it) or JSON string
        import json
        try:
            if isinstance(ing.scores, str):
                scores = json.loads(ing.scores)
            elif isinstance(ing.scores, dict):
                scores = ing.scores
            else:
                scores = {}
        except:
            scores = {}
            
        # Get the max score from the detailed breakdown as the "Hazard Score"
        # If empty or invalid, default to 5
        if scores and isinstance(scores, dict):
             # Filter out non-numeric values just in case
            numeric_scores = [v for k,v in scores.items() if isinstance(v, (int, float))]
            h_score = max(numeric_scores) if numeric_scores else 5
        else:
            h_score = 5

        # Quantity Verification Logic
        input_qty = getattr(ing, 'input_quantity', None)
        max_limit = getattr(ing, 'max_percentage', None)
        
        if input_qty is not None and max_limit is not None:
            if input_qty > max_limit:
                h_score = 10 # Force max hazard
                msg = f"Excessive {ing.name}: {input_qty}% (Limit: {max_limit}%)"
                if msg not in key_concerns:
                    key_concerns.append(msg)
                # Attach validation message for UI
                ing.quantity_validation = f"Exceeds regulation limit of {max_limit}%"
            else:
                ing.quantity_validation = f"Within safe limit ({max_limit}%)"

        
        # Check for restrictions
        if getattr(ing, "is_restricted", False):
            has_restricted = True
            if ing.name not in key_concerns:
                key_concerns.append(f"Restricted: {ing.name}")
        
        # Add to sums
        total_weighted_hazard += (h_score * weight)
        max_possible_weighted_hazard += (10 * weight)

    # Calculate base percentage
    if max_possible_weighted_hazard == 0:
        base_safety = 0
    else:
        hazard_ratio = total_weighted_hazard / max_possible_weighted_hazard
        base_safety = 100 - (hazard_ratio * 100)

    final_score = base_safety # No penalty subtraction
    final_score = max(0, final_score)
    final_score = min(100, final_score)

    # Risk Level
    if has_restricted:
        risk_level = "Not Recommended"
    elif final_score >= 80:
        risk_level = "Safe"
    elif final_score >= 50:
        risk_level = "Moderate"
    else:
        risk_level = "Hazardous"

    return {
        "overall_safety_score": round(final_score),
        "risk_level": risk_level,
        "key_concerns": key_concerns
    }
