import os
import json
from sqlalchemy.orm import Session
from app.db.models.articulation_agreements import ArticulationAgreements


def seed_articulations(db: Session):
    data_count = db.query(ArticulationAgreements).count()
    if(data_count > 0):
        print(f"Skipping seed ArticulationAgreements, {data_count} found in the model")
        return
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "seed_data", "articulations.json")
        
        with open(file_path, "r") as file:
            articulations_data = json.load(file)

        for articulation_data in articulations_data:
            articulation = ArticulationAgreements(**articulation_data)
            db.add(articulation)
        
        db.commit()
        print(f"Successfully seeded {len(articulation_data)} articulation")
    except Exception as e:
        db.rollback()
        print(f"Error seeding articulation: {str(e)}")

