from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
from routers import web_routes, concepts, reading_flows

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Qur'an Personal Understanding System (QPUS)")

# Mount static files (create dir if doesn't exist, though we made it)
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
    return {"status": "Database connection successful"}
