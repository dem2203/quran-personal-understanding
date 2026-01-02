from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Concept, Ayat, Base, ayat_concept_association
from sqlalchemy import select

def seed_concepts():
    db: Session = SessionLocal()
    
    concepts_data = [
        {
            "name": "Allah", 
            "definition": "Kainatın tek yaratıcısı, sahibi ve hakimi olan Yüce Yaratıcı. Eşi ve benzeri yoktur.",
            "verses": [(1,1), (2,255), (112,1), (112,2), (112,3), (112,4), (59,22), (59,23), (59,24)]
        },
        {
            "name": "Rahmet", 
            "definition": "Allah'ın yarattıklarına şefkat, merhamet ve ihsanda bulunması. Her şeyi kuşatan sevgi ve koruma.",
            "verses": [(1,1), (1,3), (7,156), (39,53), (21,107)]
        },
        {
            "name": "İman", 
            "definition": "Allah'a, meleklerine, kitaplarına, peygamberlerine, ahiret gününe ve kadere kalpten inanmak ve bunu dille ikrar etmek.",
            "verses": [(2,3), (2,4), (2,285), (4,136), (8,2)]
        },
        {
            "name": "Takva", 
            "definition": "Allah'a karşı sorumluluk bilinci. O'nun emirlerine uyup yasaklarından kaçınarak O'nun koruması altına girmek.",
            "verses": [(2,2), (2,197), (3,102), (49,13), (3,133)]
        },
        {
            "name": "Salih Amel", 
            "definition": "İmanla bütünleşen, iyi niyetle yapılan, Allah'ın rızasına uygun her türlü güzel iş ve davranış.",
            "verses": [(2,25), (2,82), (103,1), (103,2), (103,3), (16,97), (18,30)]
        },
        {
            "name": "Şirk", 
            "definition": "Allah'a zatında, sıfatlarında veya fiillerinde ortak koşmak. En büyük günah.",
            "verses": [(4,48), (4,116), (31,13), (39,65), (5,72)]
        },
        {
            "name": "Adalet", 
            "definition": "Hakkı sahibine vermek, her şeyi yerli yerine koymak, aşırılıktan kaçınmak ve dengeyi korumak.",
            "verses": [(4,58), (16,90), (5,8), (4,135), (57,25)]
        }
    ]

    print("Seeding concepts...")
    
    for c_data in concepts_data:
        # Check if concept exists
        concept = db.query(Concept).filter(Concept.name == c_data["name"]).first()
        if not concept:
            concept = Concept(name=c_data["name"], definition=c_data["definition"])
            db.add(concept)
            db.commit()
            db.refresh(concept)
            print(f"Created concept: {concept.name}")
        else:
            print(f"Concept exists: {concept.name}")
            
        # Map verses
        for s_num, a_num in c_data["verses"]:
            ayat = db.query(Ayat).filter(Ayat.surah_number == s_num, Ayat.ayat_number == a_num).first()
            if ayat:
                # Check association
                if concept not in ayat.concepts:
                    ayat.concepts.append(concept)
                    print(f"  Mapped {concept.name} -> {s_num}:{a_num}")
            else:
                print(f"  Warning: Ayat {s_num}:{a_num} not found")
        
        db.commit()

    print("Seeding completed.")
    db.close()

if __name__ == "__main__":
    seed_concepts()
