from app.database import SessionLocal, engine
from app.models import Base, Ingredient
import json

# Drop and create tables to ensure schema update
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # SHAMPOO ADULT DATA
    shampoo_adult = [
        # SURFACTANTS
        {"name": "Sodium Lauryl Sulfate", "scores": {"general": 4, "irritant": 4, "allergen": 2}, "description": "Strong cleanser.", "is_restricted": False},
        {"name": "Sodium Laureth Sulfate", "scores": {"general": 3, "irritant": 3, "contamination": 2}, "description": "Cleanser.", "is_restricted": False},
        
        # PRESERVATIVES
        {"name": "Parabens", "scores": {"general": 8, "endocrine_disruption": 8}, "description": "Endocrine disruptor.", "is_restricted": True, "max_percentage": 0.4, "regulation_source": "EU Regulation 1223/2009"},
        {"name": "Retinol", "scores": {"general": 6, "reprotoxic": 6}, "description": "Vitamin A derivative.", "is_restricted": False, "max_percentage": 0.3, "regulation_source": "EU Scientific Committee on Consumer Safety"},
        
        # OTHERS
        {"name": "Fragrance", "scores": {"general": 8, "allergen": 8}, "description": "Undisclosed chemicals, allergens.", "is_restricted": False},
    ]
    
    # SHAMPOO BABY DATA (Stricter scoring)
    shampoo_baby = [
        {"name": "Sodium Lauryl Sulfate", "scores": {"general": 6, "irritant": 6, "allergen": 3}, "description": "Too harsh for baby skin.", "is_restricted": False},
        {"name": "Phenoxyethanol", "scores": {"general": 5, "irritant": 5}, "description": "Can be irritating for infants.", "is_restricted": False, "max_percentage": 1.0, "regulation_source": "EU Regulation 1223/2009"},
    ]

    # SEED ADULT
    for item in shampoo_adult:
        exists = db.query(Ingredient).filter(
            Ingredient.name == item["name"],
            Ingredient.category == "shampoo",
            Ingredient.target_audience == "adult"
        ).first()
        
        if not exists:
            new_item = Ingredient(
                name=item["name"],
                scores=json.dumps(item["scores"]),
                description=item["description"],
                concerns=item.get("description", ""),
                is_restricted=item["is_restricted"],
                common_names=item["name"].lower(),
                category="shampoo",
                target_audience="adult",
                max_percentage=item.get("max_percentage"),
                regulation_source=item.get("regulation_source")
            )
            db.add(new_item)
            print(f"Added Shampoo (Adult): {item['name']}")

    # SEED BABY
    for item in shampoo_baby:
        exists = db.query(Ingredient).filter(
            Ingredient.name == item["name"],
            Ingredient.category == "shampoo",
            Ingredient.target_audience == "baby"
        ).first()
        
        if not exists:
            new_item = Ingredient(
                name=item["name"],
                scores=json.dumps(item["scores"]),
                description=item["description"],
                concerns=item.get("description", ""),
                is_restricted=item["is_restricted"],
                common_names=item["name"].lower(),
                category="shampoo",
                target_audience="baby",
                max_percentage=item.get("max_percentage"),
                regulation_source=item.get("regulation_source")
            )
            db.add(new_item)
            print(f"Added Shampoo (Baby): {item['name']}")

    db.commit()
    db.close()

if __name__ == "__main__":
    seed_data()
