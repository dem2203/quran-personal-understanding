import requests
import time
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Ayat, Base

import sys

# Set standard output to UTF-8 to avoid Windows encoding errors
sys.stdout.reconfigure(encoding='utf-8')

def get_translation_ids():
    print("Fetching translation resource IDs...")
    url = "https://api.quran.com/api/v4/resources/translations?language=tr"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    elmalili_id = None
    diyanet_id = None
    
    print("Available Turkish Translations:")
    for item in data['translations']:
        name = item['name'].lower()
        author_name = item['author_name'].lower()
        print(f"- {item['id']}: {item['name']} ({item['author_name']})")
        
        # Check for Elmalili
        if "elmalili" in name or "elmalili" in author_name:
             # Avoid simplified if possible, unless it's the only one. 
             # Usually "Elmalili Hamdi Yazir" is what we want.
             elmalili_id = item['id']
        
        # Check for Diyanet
        if "diyanet" in name or "diyanet" in author_name:
            if "işleri" in name or "isleri" in name or "işleri" in author_name or "isleri" in author_name:
                diyanet_id = item['id']
                
    return elmalili_id, diyanet_id

def import_data_from_api():
    db: Session = SessionLocal()
    
    # Check if data exists
    if db.query(Ayat).count() > 0:
        print("Data already exists. Skipping.")
        return

    try:
        elm_id, diy_id = get_translation_ids()
        print(f"Selected Translation IDs - Elmalili: {elm_id}, Diyanet: {diy_id}")
        
        if not elm_id or not diy_id:
            print("Could not find suitable translation IDs. Aborting.")
            return

        ayats_to_insert = []
        
        print("Starting import chapter by chapter...")
        for chapter in range(1, 115):
            print(f"Fetching Chapter {chapter}...")
            # Fetch all verses for the chapter
            # limit=300 covers all surahs (Baqarah is 286)
            url = f"https://api.quran.com/api/v4/verses/by_chapter/{chapter}"
            params = {
                "language": "en",
                "words": "false",
                "translations": f"{elm_id},{diy_id}",
                "fields": "text_uthmani",
                "limit": 300,
                "per_page": 300
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching chapter {chapter}: {response.text}")
                continue
                
            data = response.json()
            verses = data['verses']
            
            for v in verses:
                verse_number = v['verse_number']
                text_uthmani = v['text_uthmani']
                
                translations = v['translations']
                # Map translations by resource_id
                trans_map = {t['resource_id']: t['text'] for t in translations}
                
                t1 = trans_map.get(elm_id, "")
                t2 = trans_map.get(diy_id, "")
                
                # Clean up text if needed (sometimes HTML tags in translations)
                import re
                def clean_html(raw_html):
                    cleanr = re.compile('<.*?>')
                    return re.sub(cleanr, '', raw_html)

                t1 = clean_html(t1)
                t2 = clean_html(t2)

                ayat = Ayat(
                    surah_number=chapter,
                    ayat_number=verse_number,
                    arabic_text=text_uthmani,
                    translation_1=t1,
                    translation_2=t2
                )
                ayats_to_insert.append(ayat)
            
            # Sleep briefly to be nice to API
            # time.sleep(0.2)

        print(f"Total Ayats fetched: {len(ayats_to_insert)}")
        
        # Verify count (should be 6236)
        if len(ayats_to_insert) != 6236:
            print(f"WARNING: Expected 6236 ayats, got {len(ayats_to_insert)}")
        
        print("Inserting into database...")
        db.bulk_save_objects(ayats_to_insert)
        db.commit()
        print("Import completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    import_data_from_api()

# Alias for main.py startup
def import_quran_data():
    import_data_from_api()
