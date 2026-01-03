"""
Seed script for Mekki/Medeni information and sample reading flows.
Run this after import_data.py to add additional metadata.
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Ayat, ReadingFlow, ReadingFlowStep

# Mekki surah numbers (traditional classification)
MEKKI_SURAHS = {
    1, 6, 7, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 23, 25, 26, 27, 28, 29, 
    30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 50, 51, 52, 
    53, 54, 56, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 
    83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 100, 101, 102, 
    103, 104, 105, 106, 107, 109, 111, 112, 113, 114
}

# Sample reading flows with reflection questions
READING_FLOWS = [
    {
        "title": "Allah'ı Tanımak",
        "description": "Kur'an'da Allah kendini nasıl tanıtıyor? Sıfatları ve isimleri üzerine tefekkür.",
        "steps": [
            {"surah": 1, "ayat": 1, "question": "Besmele ile her işe başlamanın anlamı ne olabilir?"},
            {"surah": 112, "ayat": 1, "question": "Allah'ın 'Ehad' (Tek) olması hayatınızda ne anlama geliyor?"},
            {"surah": 112, "ayat": 2, "question": "'Samed' sıfatı üzerine düşünün - hiçbir şeye muhtaç olmayan..."},
            {"surah": 59, "ayat": 22, "question": "Gizliyi ve açığı bilen Allah karşısında nasıl hissediyorsunuz?"},
            {"surah": 59, "ayat": 23, "question": "Bu isimlerin her birini hayatınızda nasıl görüyorsunuz?"},
            {"surah": 2, "ayat": 255, "question": "Ayetel Kürsi'deki her cümle üzerinde ayrı ayrı düşünün."},
        ]
    },
    {
        "title": "Rahmet ve Mağfiret",
        "description": "Allah'ın rahmeti ve bağışlaması üzerine ayetler.",
        "steps": [
            {"surah": 39, "ayat": 53, "question": "Günahlardan ümitsizliğe düşmemek için bu ayet ne diyor?"},
            {"surah": 7, "ayat": 156, "question": "Rahmetin her şeyi kuşatması ne demek?"},
            {"surah": 21, "ayat": 107, "question": "Peygamber'in alemlere rahmet olması sizin için ne ifade ediyor?"},
        ]
    },
    {
        "title": "Takva Yolu",
        "description": "Takva nedir ve nasıl kazanılır?",
        "steps": [
            {"surah": 2, "ayat": 2, "question": "Kur'an muttakiler için hidayet - takva nasıl başlar?"},
            {"surah": 3, "ayat": 102, "question": "'Hakkıyla takva sahibi olmak' ne demek?"},
            {"surah": 49, "ayat": 13, "question": "Allah katında en değerli olmak takva ile mi?"},
            {"surah": 2, "ayat": 197, "question": "En iyi azık takva - dünya hayatında azığınız ne?"},
        ]
    }
]

def seed_mekki_medeni():
    """Update all ayats with Mekki/Medeni information based on surah"""
    db: Session = SessionLocal()
    
    print("Updating Mekki/Medeni information...")
    
    # Get all unique surah numbers
    surahs = db.query(Ayat.surah_number).distinct().all()
    
    for (surah_num,) in surahs:
        is_mekki = surah_num in MEKKI_SURAHS
        db.query(Ayat).filter(Ayat.surah_number == surah_num).update(
            {"is_mekki": is_mekki}, 
            synchronize_session=False
        )
        status = "Mekkî" if is_mekki else "Medenî"
        print(f"  Surah {surah_num}: {status}")
    
    db.commit()
    print("Mekki/Medeni update completed.")
    db.close()

def seed_reading_flows():
    """Create sample reading flows"""
    db: Session = SessionLocal()
    
    print("\nSeeding reading flows...")
    
    for flow_data in READING_FLOWS:
        # Check if flow exists
        existing = db.query(ReadingFlow).filter(ReadingFlow.title == flow_data["title"]).first()
        if existing:
            print(f"  Flow exists: {flow_data['title']}")
            continue
        
        flow = ReadingFlow(title=flow_data["title"], description=flow_data["description"])
        db.add(flow)
        db.flush()  # Get the ID
        
        for i, step_data in enumerate(flow_data["steps"], 1):
            # Find the ayat
            ayat = db.query(Ayat).filter(
                Ayat.surah_number == step_data["surah"],
                Ayat.ayat_number == step_data["ayat"]
            ).first()
            
            if ayat:
                step = ReadingFlowStep(
                    flow_id=flow.id,
                    order=i,
                    ayat_id=ayat.id,
                    reflection_question=step_data["question"]
                )
                db.add(step)
                print(f"    Step {i}: {step_data['surah']}:{step_data['ayat']}")
            else:
                print(f"    Warning: Ayat {step_data['surah']}:{step_data['ayat']} not found")
        
        db.commit()
        print(f"  Created flow: {flow_data['title']}")
    
    print("Reading flows seeding completed.")
    db.close()

if __name__ == "__main__":
    seed_mekki_medeni()
    seed_reading_flows()
