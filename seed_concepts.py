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
            "verses": [(1,1), (2,255), (112,1), (112,2), (112,3), (112,4), (59,22), (59,23), (59,24), (6,102), (6,103)]
        },
        {
            "name": "Rahmet", 
            "definition": "Allah'ın yarattıklarına şefkat, merhamet ve ihsanda bulunması.",
            "verses": [(1,1), (1,3), (7,156), (39,53), (21,107), (6,12), (6,54)]
        },
        {
            "name": "İman", 
            "definition": "Allah'a, meleklerine, kitaplarına, peygamberlerine ve ahirete kalpten inanmak.",
            "verses": [(2,3), (2,4), (2,285), (4,136), (8,2), (49,15), (3,179)]
        },
        {
            "name": "Takva", 
            "definition": "Allah'a karşı sorumluluk bilinci ve O'nun koruması altına girmek.",
            "verses": [(2,2), (2,197), (3,102), (49,13), (3,133), (65,2), (65,3)]
        },
        {
            "name": "Salih Amel", 
            "definition": "İmanla bütünleşen, Allah rızasına uygun güzel işler.",
            "verses": [(2,25), (2,82), (103,1), (103,2), (103,3), (16,97), (18,30), (18,107)]
        },
        {
            "name": "Şirk", 
            "definition": "Allah'a zatında veya sıfatlarında ortak koşmak. En büyük günah.",
            "verses": [(4,48), (4,116), (31,13), (39,65), (5,72), (6,151), (17,22)]
        },
        {
            "name": "Adalet", 
            "definition": "Hakkı sahibine vermek ve dengeyi korumak.",
            "verses": [(4,58), (16,90), (5,8), (4,135), (57,25), (6,152)]
        },
        {
            "name": "Sabır", 
            "definition": "Zorluklar karşısında metanet ve Allah'a güven.",
            "verses": [(2,45), (2,153), (2,155), (3,200), (16,127), (39,10), (103,3)]
        },
        {
            "name": "Dua", 
            "definition": "Allah'a yalvarmak, O'ndan yardım ve bağışlanma dilemek.",
            "verses": [(2,186), (40,60), (7,55), (7,56), (25,77), (1,5), (1,6), (1,7)]
        },
        {
            "name": "Ahiret", 
            "definition": "Ölümden sonraki ebedi hayat, hesap günü ve sonsuz yaşam.",
            "verses": [(2,4), (2,28), (3,185), (6,32), (29,64), (75,1), (82,1), (99,1)]
        },
        {
            "name": "Cennet", 
            "definition": "Müminlerin ebedi mutluluk yurdu, Allah'ın vaadi.",
            "verses": [(2,25), (3,133), (3,136), (4,57), (47,15), (55,46), (76,21)]
        },
        {
            "name": "Cehennem", 
            "definition": "İnkar edenlerin ceza yeri, ateş.",
            "verses": [(2,24), (4,56), (14,16), (22,19), (67,6), (74,26)]
        },
        {
            "name": "Peygamberler", 
            "definition": "Allah'ın insanlara hidayet için gönderdiği elçiler.",
            "verses": [(2,136), (3,84), (4,163), (6,84), (6,85), (6,86), (21,25)]
        },
        {
            "name": "Kıssalar", 
            "definition": "Kur'an'da anlatılan peygamber ve toplum hikayeleri.",
            "verses": [(7,103), (11,25), (12,3), (18,9), (26,10), (28,3)]
        },
        {
            "name": "Tevekkül", 
            "definition": "Sebeplere sarılıp sonucu Allah'a bırakmak.",
            "verses": [(3,159), (5,11), (8,49), (12,67), (14,12), (65,3)]
        },
        {
            "name": "Namaz", 
            "definition": "Günlük beş vakit ibadet, kulun Allah'a yaklaşması.",
            "verses": [(2,43), (2,238), (4,103), (11,114), (17,78), (29,45)]
        },
        {
            "name": "Zekat/İnfak", 
            "definition": "Maldan Allah yolunda harcama, ihtiyaç sahiplerine yardım.",
            "verses": [(2,43), (2,195), (2,261), (2,267), (2,271), (9,60)]
        },
        {
            "name": "Tövbe", 
            "definition": "Günahlardan pişmanlık duyup Allah'a dönmek.",
            "verses": [(4,17), (4,110), (6,54), (25,70), (39,53), (66,8)]
        },
        {
            "name": "Yaratılış", 
            "definition": "Allah'ın kainatı, insanı ve tüm varlıkları yaratması.",
            "verses": [(2,30), (7,54), (15,26), (23,12), (32,7), (55,3), (96,1), (96,2)]
        },
        {
            "name": "Aile", 
            "definition": "Evlilik, ebeveynler ve aile ilişkileri.",
            "verses": [(2,228), (4,1), (4,19), (17,23), (30,21), (31,14), (46,15)]
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
