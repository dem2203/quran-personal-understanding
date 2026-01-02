from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Ayat, Reflection
from utils import get_surah_list, SURAH_NAMES

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "surahs": get_surah_list()
    })

@router.get("/surah/{surah_number}", response_class=HTMLResponse)
async def read_surah(request: Request, surah_number: int, db: Session = Depends(get_db)):
    ayats = db.query(Ayat).filter(Ayat.surah_number == surah_number).order_by(Ayat.ayat_number).all()
    surah_name = SURAH_NAMES.get(surah_number, f"Sure {surah_number}")
    
    return templates.TemplateResponse("surah_detail.html", {
        "request": request,
        "surah_number": surah_number,
        "surah_name": surah_name,
        "ayats": ayats
    })

@router.post("/reflection/add", response_class=HTMLResponse)
def add_reflection(
    request: Request, 
    ayat_id: int = Form(...), 
    content: str = Form(...),
    next_url: str = Form(...),
    db: Session = Depends(get_db)
):
    reflection = Reflection(ayat_id=ayat_id, text_content=content)
    db.add(reflection)
    db.commit()
    
    # Ideally return a partial or redirect. For MVP redirect back.
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=next_url, status_code=303)
