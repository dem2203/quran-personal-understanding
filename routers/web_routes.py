from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Ayat, Reflection, Favorite, UserPreference
from utils import get_surah_list, SURAH_NAMES

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Helper to get/set user preferences
def get_preference(db: Session, key: str) -> str:
    pref = db.query(UserPreference).filter(UserPreference.key == key).first()
    return pref.value if pref else None

def set_preference(db: Session, key: str, value: str):
    pref = db.query(UserPreference).filter(UserPreference.key == key).first()
    if pref:
        pref.value = value
    else:
        pref = UserPreference(key=key, value=value)
        db.add(pref)
    db.commit()

@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request, db: Session = Depends(get_db)):
    # Get last read position
    last_surah = get_preference(db, "last_read_surah")
    last_ayat = get_preference(db, "last_read_ayat")
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "surahs": get_surah_list(),
        "last_surah": int(last_surah) if last_surah else None,
        "last_ayat": int(last_ayat) if last_ayat else None
    })

@router.get("/surah/{surah_number}", response_class=HTMLResponse)
async def read_surah(request: Request, surah_number: int, db: Session = Depends(get_db)):
    from models import NuzulSebebi
    
    ayats = db.query(Ayat).filter(Ayat.surah_number == surah_number).order_by(Ayat.ayat_number).all()
    surah_name = SURAH_NAMES.get(surah_number, f"Sure {surah_number}")
    
    # Get favorite ayat IDs for this surah
    favorite_ids = set(
        f.ayat_id for f in db.query(Favorite).join(Ayat).filter(Ayat.surah_number == surah_number).all()
    )
    
    # Get Nuzul Sebebi data for this surah (indexed by ayat number)
    nuzul_list = db.query(NuzulSebebi).filter(NuzulSebebi.surah_number == surah_number).all()
    nuzul_map = {ns.ayat_number: ns.text_en for ns in nuzul_list}
    
    # Update last read position
    set_preference(db, "last_read_surah", str(surah_number))
    if ayats:
        set_preference(db, "last_read_ayat", str(ayats[0].ayat_number))
    
    return templates.TemplateResponse("surah_detail.html", {
        "request": request,
        "surah_number": surah_number,
        "surah_name": surah_name,
        "ayats": ayats,
        "favorite_ids": favorite_ids,
        "nuzul_map": nuzul_map
    })

@router.post("/reflection/add", response_class=HTMLResponse)
def add_reflection(
    request: Request, 
    ayat_id: int = Form(...), 
    content: str = Form(...),
    next_url: str = Form(...),
    concept_tag: str = Form(None),
    db: Session = Depends(get_db)
):
    reflection = Reflection(ayat_id=ayat_id, text_content=content, concept_tag=concept_tag)
    db.add(reflection)
    db.commit()
    return RedirectResponse(url=next_url, status_code=303)

@router.get("/reflections", response_class=HTMLResponse)
async def read_reflections(request: Request, db: Session = Depends(get_db)):
    reflections = db.query(Reflection).order_by(Reflection.created_at.desc()).all()
    return templates.TemplateResponse("reflections.html", {
        "request": request,
        "reflections": reflections
    })

@router.post("/favorite/toggle")
def toggle_favorite(
    ayat_id: int = Form(...),
    next_url: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(Favorite).filter(Favorite.ayat_id == ayat_id).first()
    if existing:
        db.delete(existing)
    else:
        db.add(Favorite(ayat_id=ayat_id))
    db.commit()
    return RedirectResponse(url=next_url, status_code=303)

@router.get("/favorites", response_class=HTMLResponse)
async def read_favorites(request: Request, db: Session = Depends(get_db)):
    favorites = db.query(Favorite).order_by(Favorite.created_at.desc()).all()
    return templates.TemplateResponse("favorites.html", {
        "request": request,
        "favorites": favorites
    })

