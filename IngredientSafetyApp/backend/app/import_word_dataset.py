import os
import sys
import json
import re

# Add the parent directory to sys.path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Ingredient, Base

def extract_json_object(text):
    # Extracts the first \{ ... \} matching balanced braces
    start = text.find('{')
    if start == -1:
        return ""
    
    count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            count += 1
        elif text[i] == '}':
            count -= 1
            if count == 0:
                return text[start:i+1]
    return ""

def parse_dataset(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []

    # Split the blocks based on the pattern: Name followed by {
    # We use a regex to find all blocks that look like a title followed by a JSON object
    # The name should contain at least one letter or number
    pattern = r'([A-Za-z0-9][A-Za-z0-9\s\-,()]+)\n\s*\{'
    matches = list(re.finditer(pattern, content))
    
    ingredients_data = []
    
    for i in range(len(matches)):
        start_idx = matches[i].start()
        # The block ends where the next match starts, or at the end of the file
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
        
        block = content[start_idx:end_idx].strip()
        lines = block.split('\n')
        name = lines[0].strip()
        
        json_str = block[len(name):].strip()
        if not json_str.startswith('{'):
           json_str = '{' + json_str

        # Clean it up first
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Now strictly extract the JSON object
        json_str = extract_json_object(json_str)

        if not json_str:
            continue
            
        try:
            data = json.loads(json_str)
            if isinstance(data, dict):
                ingredients_data.append({"name": name, "data": data})
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for ingredient '{name}': {e}")
            pass

    return ingredients_data

def import_word_dataset():
    dataset_path = r'C:\Users\DELL\Downloads\dataset_dump.txt'
    
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found.")
        return

    print("Parsing dataset...")
    parsed_ingredients = parse_dataset(dataset_path)
    
    if not parsed_ingredients:
        print("No valid ingredients found to import.")
        return
        
    print(f"Successfully parsed {len(parsed_ingredients)} ingredients.")

    db = SessionLocal()
    
    print("Clearing existing ingredients from the database...")
    try:
        # Recreating the Database Schema to apply any new columns
        print("Recreating existing database schema...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("Database schema updated.")
    except Exception as e:
        print(f"Error recreating database schema: {e}")
        db.close()
        return
        
    print("Importing new dataset...")
    
    count_created = 0
    
    for item in parsed_ingredients:
        name = item['name']
        data = item['data']
        
        if not isinstance(data, dict):
            print(f"Skipping malformed data for item: {name}")
            continue
            
        metadata = data.get('ingredient_metadata', {})
        safety = data.get('safety_scoring_engine', {})
        regulatory = data.get('regulatory_guardrails', {})
        user_facing = data.get('user_facing_content', {})
        alternatives_raw = data.get('actionable_alternatives', {})
        
        # Additional safety check for malformed data
        if not isinstance(metadata, dict) or not isinstance(safety, dict):
            print(f"Skipping incorrectly structured item: {name}")
            continue
        if not isinstance(regulatory, dict): regulatory = {}
        if not isinstance(user_facing, dict): user_facing = {}
        if not isinstance(alternatives_raw, dict): alternatives_raw = {}
        
        # Map fields safely
        common_names_list = metadata.get('common_aliases', [])
        common_names = ", ".join(common_names_list) if isinstance(common_names_list, list) else str(common_names_list)
        
        hazard_weights = safety.get('hazard_weights', {})
        scores = json.dumps(hazard_weights) if isinstance(hazard_weights, dict) else "{}"
        
        alternatives_json = json.dumps(alternatives_raw) if alternatives_raw else None
        
        description = f"{metadata.get('function', '')}. Origin: {metadata.get('origin', '')}"
        concerns = f"Rating: {safety.get('overall_safety_rating')}, {safety.get('hazard_level')}. {safety.get('note', '')} {user_facing.get('risk_analysis', '')}"
        
        is_restricted = regulatory.get('is_banned', False)
        
        # Use max_allowable_percentage from the first government limit if available
        gov_limits = regulatory.get('government_limits', [])
        regulation_source = ""
        max_limit_str = ""
        if isinstance(gov_limits, list) and len(gov_limits) > 0:
             gov = gov_limits[0]
             if isinstance(gov, dict):
                 regulation_source = gov.get('authority', '')
                 if 'EU Cosmetics Regulation' in regulation_source or 'EU' in regulation_source:
                    regulation_source = "EU" # simplify
                    
                 max_limit_str = gov.get('max_allowable_percentage', '')
        
        # Parse percentage roughly if possible
        max_percentage = None
        if max_limit_str and isinstance(max_limit_str, str):
            match = re.search(r'([\d.]+)\s*%', max_limit_str)
            if match:
                try:
                    max_percentage = float(match.group(1))
                except ValueError:
                    pass
                    
        raw_data_json = json.dumps(data) if data else None
                    
        new_ing = Ingredient(
            name=metadata.get('name', name), # Prefer name from metadata if it exists
            common_names=common_names,
            scores=scores,
            description=description,
            concerns=concerns,
            is_restricted=bool(is_restricted),
            category="shampoo", # Defaulting as per original schema
            target_audience="all",
            max_percentage=max_percentage,
            regulation_source=regulation_source,
            regulation=regulatory.get('global_status', ''),
            alternatives=alternatives_json,
            raw_data=raw_data_json
        )
        
        db.add(new_ing)
        count_created += 1
        
    db.commit()
    print(f"Success! Inserted {count_created} new ingredients into the database.")
    
    db.close()

if __name__ == "__main__":
    import_word_dataset()
