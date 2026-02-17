import csv
import os
import sys
import json

# Add the parent directory to sys.path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Ingredient

def import_regulations():
    csv_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'regulations.csv')
    
    if not os.path.exists(csv_file_path):
        print(f"Error: {csv_file_path} not found.")
        return

    db = SessionLocal()
    
    print(f"Importing regulations from {csv_file_path}...")
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            count_updated = 0
            count_created = 0
            
            for row in reader:
                name = row['Substance Name'].strip()
                try:
                    max_limit = float(row['Max Concentration'])
                except ValueError:
                    print(f"Skipping {name}: Invalid concentration '{row['Max Concentration']}'")
                    continue
                    
                source = row['Regulation Source'].strip()
                
                # Check if ingredient exists (case-insensitive search recommended, but simple match for now)
                # We'll update ALL matching ingredients (adult, baby, shampoo, etc.)
                ingredients = db.query(Ingredient).filter(Ingredient.name == name).all()
                
                if ingredients:
                    for ing in ingredients:
                        ing.max_percentage = max_limit
                        ing.regulation_source = source
                        # Update description if empty
                        if not ing.description:
                             ing.description = f"Regulated ingredient per {source}"
                        count_updated += 1
                else:
                    # Create new ingredient if not found
                    # Use a default structure for scores
                    default_scores = json.dumps({"general": 5, "unknown": 5}) 
                    new_ing = Ingredient(
                        name=name,
                        scores=default_scores,
                        description=f"Imported from regulation list. Source: {source}",
                        concerns=f"Maximum allowed concentration: {max_limit}%",
                        is_restricted=False, 
                        common_names=name.lower(),
                        category="all",
                        target_audience="all",
                        max_percentage=max_limit,
                        regulation_source=source
                    )
                    db.add(new_ing)
                    count_created += 1
            
            db.commit()
            print(f"Success! Updated {count_updated} records, Created {count_created} new records.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_regulations()
