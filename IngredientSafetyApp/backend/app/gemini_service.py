import random

def get_ingredient_details(ingredient_name, category="shampoo", target_audience="adult", quantity=None):
    """
    Mock function to simulate Gemini API response.
    Returns markdown formatted text.
    """
    
    # Generic templates based on safety
    safe_templates = [
        "is generally considered **safe** for use in cosmetics.",
        "is a common and well-tolerated ingredient.",
        "has a long history of safe use in personal care products."
    ]
    
    caution_templates = [
        "should be used with **caution**.",
        "may cause irritation in sensitive individuals.",
        "has some regulatory restrictions due to potential sensitization."
    ]
    
    unsafe_templates = [
        "is **not recommended**, especially for sensitive groups.",
        "has been linked to potential health concerns.",
        "is restricted in many regions due to safety risks."
    ]
    
    # Simple keyword-based logic for the mock
    name_lower = ingredient_name.lower()
    
    if any(x in name_lower for x in ['water', 'aqua', 'extract', 'oil', 'glycerin']):
        safety_text = random.choice(safe_templates)
        verdict = "Safe"
    elif any(x in name_lower for x in ['sulfate', 'fragrance', 'parfum', 'alcohol']):
        safety_text = random.choice(caution_templates)
        verdict = "Moderate"
    elif any(x in name_lower for x in ['paraben', 'retinol', 'triclosan', 'formaldehyde']):
        safety_text = random.choice(unsafe_templates)
        verdict = "Hazardous"
    else:
        safety_text = "requires more data for a definitive safety conclusion."
        verdict = "Unknown"

    # Context-aware content
    audience_context = ""
    if target_audience == "baby":
        audience_context = f"\n\n### 👶 For Babies:\nSince this product is for **babies**, extra caution is advised. Their skin is thinner and more permeable. "
        if verdict in ["Moderate", "Hazardous"]:
            audience_context += f"**{ingredient_name}** is generally recommended to be avoided in baby products to prevent irritation or systemic absorption."
        else:
            audience_context += f"**{ingredient_name}** is likely gentle enough, but always patch test."
            
    elif target_audience == "adult":
        audience_context = f"\n\n### 👤 For Adults:\nFor standard adult use, this ingredient is evaluated based on healthy skin tolerance. "
        if verdict == "Hazardous":
            audience_context += "However, considering the potential long-term effects, safer alternatives might be preferable."

    # Quantity content
    # Mock some regulation limits for demo purposes
    mock_limits = {
        "retinol": 0.3,
        "salicylic acid": 2.0,
        "glycolic acid": 10.0,
        "parabens": 0.4,
        "phenoxyethanol": 1.0
    }
    
    limit = mock_limits.get(name_lower, 1.0) # Default 1.0% if unknown
    
    qty_context = f"\n\n### ⚖️ Regulatory Compliance\n"
    qty_context += f"**Government Recommended Limit**: Maximum **{limit}%** in leave-on products (based on EU Regulation 1223/2009).\n"
    
    if quantity:
        qty_context += f"**Your Product's Concentration**: **{quantity}%**\n\n"
        if quantity > limit:
             qty_context += f"⚠️ **WARNING**: This concentration EXCEEDS the recommended safe limit by **{round(quantity - limit, 2)}%**.\n"
             qty_context += f"\n**Potential Risks at this Level:**\n"
             qty_context += f"*   **Severe Irritation**: High likelihood of redness, peeling, and burning sensation.\n"
             qty_context += f"*   **Systemic Toxicity**: Potential for ingredient to be absorbed into the bloodstream.\n"
             qty_context += f"*   **Allergic Sensitization**: Increased risk of developing a permanent allergy to this ingredient.\n"
        else:
             qty_context += f"✅ **SAFE**: This concentration is within the allowable safety limits.\n"
    else:
        qty_context += f"**Analysis**: Please check if your product label specifies a concentration. If it exceeds {limit}%, it may be unsafe."

    # Final Markdown Response
    response = f"""
## Analysis of **{ingredient_name}**
**Verdict**: {verdict}

**{ingredient_name}** {safety_text} It is commonly found in {category} products.

{audience_context}
{qty_context}

---
*Disclaimer: This is a generated summary for educational purposes.*
"""
    return response.strip()
