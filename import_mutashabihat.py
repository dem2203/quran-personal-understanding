"""
Import Mutashabihat (Similar Verses) data from Waqar144/Quran_Mutashabihat_Data
This data helps identify verses that are similar in wording (useful for memorization)
"""
import requests
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Ayat

# Association table for similar verses
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from database import Base

similar_ayat_association = Table(
    "similar_ayat",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source_surah", Integer, nullable=False),
    Column("source_ayat", Integer, nullable=False),
    Column("target_surah", Integer, nullable=False),
    Column("target_ayat", Integer, nullable=False),
)

# Surah ayat counts for converting absolute ayah number to surah:ayah
SURAH_AYAT_COUNTS = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128, 111,
    110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73, 54, 45,
    83, 182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
    78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20,
    56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21,
    11, 8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6
]

def absolute_to_surah_ayat(absolute_num):
    """Convert absolute ayah number (1-6236) to (surah, ayat)"""
    cumulative = 0
    for surah_idx, count in enumerate(SURAH_AYAT_COUNTS):
        if cumulative + count >= absolute_num:
            return (surah_idx + 1, absolute_num - cumulative)
        cumulative += count
    return (114, absolute_num - cumulative)

def import_mutashabihat():
    """Import similar verses data"""
    db: Session = SessionLocal()
    
    # Check if table exists and has data
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        if 'similar_ayat' in inspector.get_table_names():
            result = db.execute("SELECT COUNT(*) FROM similar_ayat").fetchone()
            if result[0] > 0:
                print("Similar verses data already exists. Skipping.")
                db.close()
                return
    except:
        pass
    
    # Create table if not exists
    similar_ayat_association.create(engine, checkfirst=True)
    
    print("Downloading Mutashabihat data...")
    url = "https://raw.githubusercontent.com/Waqar144/Quran_Mutashabihat_Data/master/mutashabiha_data.json"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error downloading data: {e}")
        db.close()
        return
    
    print("Processing similar verses...")
    total_pairs = 0
    
    for juz_key, entries in data.items():
        for entry in entries:
            src = entry.get("src", {})
            muts = entry.get("muts", [])
            
            # Handle source ayah (can be single or range)
            src_ayah = src.get("ayah")
            if isinstance(src_ayah, list):
                src_ayah = src_ayah[0]  # Take first of range
            
            if not src_ayah:
                continue
            
            src_surah, src_ayat = absolute_to_surah_ayat(src_ayah)
            
            for mut in muts:
                target_ayah = mut.get("ayah")
                if isinstance(target_ayah, list):
                    target_ayah = target_ayah[0]
                
                if not target_ayah:
                    continue
                
                target_surah, target_ayat = absolute_to_surah_ayat(target_ayah)
                
                # Insert the relationship
                db.execute(
                    similar_ayat_association.insert().values(
                        source_surah=src_surah,
                        source_ayat=src_ayat,
                        target_surah=target_surah,
                        target_ayat=target_ayat
                    )
                )
                total_pairs += 1
    
    db.commit()
    print(f"Imported {total_pairs} similar verse pairs.")
    db.close()

if __name__ == "__main__":
    import_mutashabihat()
