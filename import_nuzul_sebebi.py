"""
Import Nuzul Sebebi (Asbab al-Nuzul) data from spa5k/tafsir_api
Source: Al-Wahidi's Asbab al-Nuzul (English translation)
"""
import requests
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import NuzulSebebi, Ayat

BASE_URL = "https://raw.githubusercontent.com/spa5k/tafsir_api/main/tafsir/en-asbab-al-nuzul-by-al-wahidi"

def import_nuzul_sebebi():
    """Import revelation reasons from Al-Wahidi"""
    db: Session = SessionLocal()
    
    # Check if data exists
    if db.query(NuzulSebebi).count() > 0:
        print("Nuzul Sebebi data already exists. Skipping.")
        db.close()
        return
    
    print("Importing Asbab al-Nuzul (Nuzul Sebebi) data...")
    
    total_imported = 0
    
    for surah in range(1, 115):
        url = f"{BASE_URL}/{surah}.json"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print(f"  Surah {surah}: No data available")
                continue
            
            data = response.json()
            ayahs = data.get("ayahs", [])
            
            for ayah_data in ayahs:
                ayat_num = ayah_data.get("ayah")
                text = ayah_data.get("text", "")
                
                if text and text.strip():
                    ns = NuzulSebebi(
                        surah_number=surah,
                        ayat_number=ayat_num,
                        text_en=text.strip(),
                        source="Al-Wahidi"
                    )
                    db.add(ns)
                    total_imported += 1
            
            db.commit()
            print(f"  Surah {surah}: {len(ayahs)} entries")
            
        except Exception as e:
            print(f"  Error fetching surah {surah}: {e}")
            continue
    
    print(f"Nuzul Sebebi import completed. Total entries: {total_imported}")
    db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    import_nuzul_sebebi()
