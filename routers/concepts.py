from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Concept

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/concepts", response_class=HTMLResponse)
async def read_concepts(request: Request, db: Session = Depends(get_db)):
    concepts = db.query(Concept).all()
    return templates.TemplateResponse("concept_list.html", {
        "request": request, 
        "concepts": concepts
    })

@router.get("/concept/{concept_id}", response_class=HTMLResponse)
async def read_concept_detail(request: Request, concept_id: int, db: Session = Depends(get_db)):
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    # Loading relationship eagerly or lazily (lazy is default)
    # The template will access concept.ayats
    
    return templates.TemplateResponse("concept_detail.html", {
        "request": request,
        "concept": concept
    })
