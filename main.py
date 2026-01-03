from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from database import engine, Base, get_db, SessionLocal
import models
from routers import web_routes, concepts, reading_flows

# Create tables
Base.metadata.create_all(bind=engine)

def run_initial_import():
    """Run data import if database is empty"""
    from models import Ayat
    db = SessionLocal()
    try:
        ayat_count = db.query(Ayat).count()
        if ayat_count == 0:
            print("Database is empty. Running initial data import...")
            
            # Import Quran data
            try:
                from import_data import import_quran_data
                import_quran_data()
                print("Quran data import completed.")
            except Exception as e:
                print(f"Error importing Quran data: {e}")
            
            # Import concepts
            try:
                from seed_concepts import seed_concepts
                seed_concepts()
                print("Concepts seeding completed.")
            except Exception as e:
                print(f"Error seeding concepts: {e}")
            
            # Import Mekki/Medeni and reading flows
            try:
                from seed_mekki_flows import seed_mekki_medeni, seed_reading_flows
                seed_mekki_medeni()
                seed_reading_flows()
                print("Mekki/Medeni and reading flows completed.")
            except Exception as e:
                print(f"Error seeding Mekki/flows: {e}")
        else:
            print(f"Database has {ayat_count} ayats. Skipping import.")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    run_initial_import()
    yield
    # Shutdown (nothing to cleanup)

app = FastAPI(title="Qur'an Personal Understanding System (QPUS)", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(web_routes.router)
app.include_router(concepts.router)
app.include_router(reading_flows.router)

@app.get("/api/status")
def read_root():
    return {"message": "QPUS API is running"}

@app.get("/db-check")
def read_db_check(db: Session = Depends(get_db)):
    count = db.query(models.Ayat).count()
    return {"status": "Database connection successful", "ayat_count": count}

