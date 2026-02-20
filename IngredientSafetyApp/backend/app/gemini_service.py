import json
from .database import SessionLocal
from .models import Ingredient
import difflib

def get_ingredient_details(ingredient_name, category="shampoo", target_audience="adult", quantity=None):
    """
    Fetches comprehensive ingredient details directly from the newly uploaded dataset
    stored in the SQLite database and formats it into rich Markdown.
    """
    db = SessionLocal()
    
    try:
        # 1. Exact or Fuzzy match the ingredient
        cleaned_name = ingredient_name.strip().lower()
        
        # Try exact first
        ingredient = db.query(Ingredient).filter(Ingredient.name.ilike(cleaned_name)).first()
        
        # Try fuzzy match if not found
        if not ingredient:
             all_ings = db.query(Ingredient).all()
             name_map = {ing.name.lower(): ing for ing in all_ings}
             matches = difflib.get_close_matches(cleaned_name, name_map.keys(), n=1, cutoff=0.7)
             if matches:
                 ingredient = name_map[matches[0]]
                 
        if not ingredient:
             return f"## Analysis of **{ingredient_name}**\n\nNo detailed safety record was found for this ingredient in our current database."

        # 2. Extract and format the data
        # Handle scores which might be JSON strings or empty
        scores = {}
        if ingredient.scores:
            if isinstance(ingredient.scores, str):
                try:
                    scores = json.loads(ingredient.scores)
                except json.JSONDecodeError:
                    pass
            elif isinstance(ingredient.scores, dict):
                scores = ingredient.scores

        # Determine Primary Verdict based on scores
        # We assume ratings over 5 indicate higher concern based on the updated dataset
        max_score = 0
        if scores:
             numeric_scores = [v for v in scores.values() if isinstance(v, (int, float))]
             if numeric_scores:
                 max_score = max(numeric_scores)
                 
        verdict = "Low Risk"
        alert_icon = "✅"
        if max_score >= 7 or ingredient.is_restricted:
             verdict = "High Risk / Hazardous"
             alert_icon = "🚨"
        elif max_score >= 4:
             verdict = "Moderate Risk"
             alert_icon = "⚠️"

        # Construct the context paragraphs
        audience_context = ""
        if target_audience == "baby":
            audience_context = f"**For Babies:** Extra caution advised due to thinner, more permeable skin. "
            if max_score >= 4:
                audience_context += "Generally recommended to be avoided in baby products."
            else:
                 audience_context += "Likely safe, but patch testing is always recommended."
                 
        description_text = ingredient.description if ingredient.description else "A common cosmetic or cleansing ingredient."
        concerns_text = ingredient.concerns if ingredient.concerns else "No major specific concerns listed."

        # Regulation limits formatting
        qty_context = f"### ⚖️ Regulatory Compliance\n"
        limit_text = ingredient.max_percentage if ingredient.max_percentage else "No strict numerical limit specified."
        source_text = ingredient.regulation_source if ingredient.regulation_source else ingredient.regulation
        
        qty_context += f"**Government Recommended Limit**: {limit_text}% (Source: {source_text})\n\n"
        
        if quantity and ingredient.max_percentage:
             qty_context += f"**Your Product's Concentration**: **{quantity}%**\n"
             if quantity > ingredient.max_percentage:
                 qty_context += f"⚠️ **WARNING**: EXCEEDS safe limit by **{round(quantity - ingredient.max_percentage, 2)}%**.\n"
             else:
                  qty_context += f"✅ **SAFE**: Within allowable safety limits.\n"
        elif quantity:
             qty_context += f"**Your Product's Concentration**: **{quantity}%** (No strict upper limit found for direct comparison).\n"

        # Detailed breakdown of specific hazard scores from the new dataset
        hazard_details = "\n### 🧬 Specific Hazard Ratings (0-10)\n"
        if scores:
             for key, val in scores.items():
                  # Format the key nicely
                  formatted_key = str(key).replace('_', ' ').capitalize()
                  hazard_details += f"* **{formatted_key}**: {val}\n"
        else:
             hazard_details += "No specific granular hazard ratings available.\n"
             
        # Extraction of ALL missing fields from raw_data
        extra_context = ""
        if getattr(ingredient, 'raw_data', None):
             try:
                 raw = json.loads(ingredient.raw_data)
                 meta = raw.get('ingredient_metadata', {})
                 reg = raw.get('regulatory_guardrails', {})
                 
                 # Technical Identifiers
                 cas = meta.get('cas_number')
                 iid = meta.get('ingredient_id')
                 if cas or iid:
                     extra_context += "### 🔬 Technical Identifiers\n"
                     if cas: extra_context += f"*   **CAS Number**: `{cas}`\n"
                     if iid: extra_context += f"*   **Ingredient ID**: `{iid}`\n"
                     extra_context += "\n"
                     
                 # Environmental & Ethics
                 env = raw.get('environmental_impact', {})
                 is_vegan = raw.get('is_vegan')
                 certs = raw.get('certifications', [])
                 
                 if env or is_vegan is not None or certs:
                     extra_context += "### 🌍 Environmental & Ethics\n"
                     if is_vegan is not None:
                         extra_context += f"*   **Vegan**: {'Yes ✅' if is_vegan else 'No ❌'}\n"
                     if env and isinstance(env, dict):
                         for k, v in env.items():
                             extra_context += f"*   **{str(k).replace('_', ' ').capitalize()}**: {v}\n"
                     if certs and isinstance(certs, list):
                         extra_context += f"*   **Certifications**: {', '.join(certs)}\n"
                     extra_context += "\n"
                     
                 # Full Government Limits
                 gov_limits = reg.get('government_limits', [])
                 if len(gov_limits) > 1: # We already showed the first one in qty_context
                     extra_context += "### ⚖️ Additional Government Constraints\n"
                     for gl in gov_limits[1:]: # Skip the first one
                         if isinstance(gl, dict):
                             auth = gl.get('authority', 'Unknown')
                             limit = gl.get('max_allowable_percentage', 'N/A')
                             n = gl.get('note', '')
                             extra_context += f"*   **{auth}**: {limit} - {n}\n"
                     extra_context += "\n"
                     
             except json.JSONDecodeError:
                 pass

        # Green Alternatives Logic
        green_context = ""
        if getattr(ingredient, 'alternatives', None):
             try:
                 alts_data = json.loads(ingredient.alternatives)
                 if alts_data and isinstance(alts_data, dict):
                     suggestions = alts_data.get('suggestions', [])
                     if suggestions:
                         green_context += "## 🌱 Green Alternatives\n"
                         green_context += f"*{alts_data.get('pivot_reason', 'Consider these safer options.')}*\n\n"
                         for alt in suggestions:
                             alt_name = alt.get('alt_name', 'Unknown Alternative')
                             benefit = alt.get('benefit', '')
                             green_context += f"*   **{alt_name}**: {benefit}\n"
             except json.JSONDecodeError:
                 pass
             
        # Aliases
        alias_text = ""
        if ingredient.common_names and ingredient.common_names.lower() != ingredient.name.lower():
            alias_text = f"*(Also known as: {ingredient.common_names})*"

        # Final Markdown Response
        response = f"""
## Analysis of **{ingredient.name}**
{alias_text}

**Verdict**: {alert_icon} **{verdict}**

### 📖 Overview
**{ingredient.name}** is generally used as a {description_text}

**Safety Summary:** {concerns_text}

{audience_context}

{qty_context}
{hazard_details}

{extra_context}
{green_context}

---
*Data extracted securely from updated ingredient safety database.*
"""
        return response.strip()

    except Exception as e:
        print(f"Error fetching details for {ingredient_name}: {e}")
        return f"## Analysis of **{ingredient_name}**\n\nAn error occurred while fetching details from the database."
    finally:
        db.close()
