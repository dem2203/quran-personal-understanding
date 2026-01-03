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
    from sqlalchemy import text
    
    ayats = db.query(Ayat).filter(Ayat.surah_number == surah_number).order_by(Ayat.ayat_number).all()
    surah_name = SURAH_NAMES.get(surah_number, f"Sure {surah_number}")
    
    # Get favorite ayat IDs for this surah
    favorite_ids = set(
        f.ayat_id for f in db.query(Favorite).join(Ayat).filter(Ayat.surah_number == surah_number).all()
    )
    
    # Get Nuzul Sebebi data for this surah (indexed by ayat number)
    nuzul_list = db.query(NuzulSebebi).filter(NuzulSebebi.surah_number == surah_number).all()
    nuzul_map = {ns.ayat_number: ns.text_en for ns in nuzul_list}
    
    # Get Similar Verses (Mutashabihat) for this surah - word similarity
    similar_map = {}
    try:
        result = db.execute(text(
            "SELECT source_ayat, target_surah, target_ayat FROM similar_ayat WHERE source_surah = :surah"
        ), {"surah": surah_number})
        for row in result:
            source_ayat = row[0]
            if source_ayat not in similar_map:
                similar_map[source_ayat] = []
            similar_map[source_ayat].append({"surah": row[1], "ayat": row[2]})
    except:
        pass  # Table may not exist yet
    
    # REVERSE: Get verses that reference THIS surah's verses (bidirectional)
    referenced_by_map = {}
    try:
        result = db.execute(text(
            "SELECT target_ayat, source_surah, source_ayat FROM similar_ayat WHERE target_surah = :surah"
        ), {"surah": surah_number})
        for row in result:
            target_ayat = row[0]
            if target_ayat not in referenced_by_map:
                referenced_by_map[target_ayat] = []
            referenced_by_map[target_ayat].append({"surah": row[1], "ayat": row[2], "type": "kelime"})
        
        # Also add semantic reverse references
        result2 = db.execute(text(
            "SELECT target_ayat, source_surah, source_ayat FROM semantic_similarity WHERE target_surah = :surah"
        ), {"surah": surah_number})
        for row in result2:
            target_ayat = row[0]
            if target_ayat not in referenced_by_map:
                referenced_by_map[target_ayat] = []
            referenced_by_map[target_ayat].append({"surah": row[1], "ayat": row[2], "type": "anlam"})
    except:
        pass
    
    # Get Semantic Similarity (QurSim) for this surah - meaning similarity
    semantic_map = {}
    try:
        result = db.execute(text(
            "SELECT source_ayat, target_surah, target_ayat, similarity_degree FROM semantic_similarity WHERE source_surah = :surah"
        ), {"surah": surah_number})
        for row in result:
            source_ayat = row[0]
            if source_ayat not in semantic_map:
                semantic_map[source_ayat] = []
            semantic_map[source_ayat].append({"surah": row[1], "ayat": row[2], "degree": row[3]})
    except:
        pass  # Table may not exist yet
    
    # Get Tafsir References for this surah
    tafsir_map = {}
    try:
        result = db.execute(text(
            "SELECT source_ayat, target_surah, target_ayat, mufassir, note_tr FROM tafsir_reference WHERE source_surah = :surah"
        ), {"surah": surah_number})
        for row in result:
            source_ayat = row[0]
            if source_ayat not in tafsir_map:
                tafsir_map[source_ayat] = []
            tafsir_map[source_ayat].append({
                "surah": row[1], 
                "ayat": row[2], 
                "mufassir": row[3],
                "note": row[4]
            })
    except:
        pass
    
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
        "nuzul_map": nuzul_map,
        "similar_map": similar_map,
        "semantic_map": semantic_map,
        "referenced_by_map": referenced_by_map,
        "tafsir_map": tafsir_map,
        "surah_names": SURAH_NAMES
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

@router.get("/verse-graph/{surah_number}/{ayat_number}", response_class=HTMLResponse)
async def verse_graph(request: Request, surah_number: int, ayat_number: int, db: Session = Depends(get_db)):
    """Interactive D3.js graph showing verse relationships"""
    from sqlalchemy import text
    import json
    
    surah_name = SURAH_NAMES.get(surah_number, f"Sure {surah_number}")
    
    nodes = []
    links = []
    node_ids = set()
    
    # Center node
    center_id = f"{surah_number}:{ayat_number}"
    nodes.append({
        "id": center_id,
        "label": center_id,
        "surah": surah_number,
        "ayat": ayat_number,
        "isCenter": True
    })
    node_ids.add(center_id)
    
    # Get outgoing kelime similarity (this verse -> others)
    try:
        result = db.execute(text(
            "SELECT target_surah, target_ayat FROM similar_ayat WHERE source_surah = :s AND source_ayat = :a"
        ), {"s": surah_number, "a": ayat_number})
        for row in result:
            target_id = f"{row[0]}:{row[1]}"
            if target_id not in node_ids:
                nodes.append({"id": target_id, "label": target_id, "surah": row[0], "ayat": row[1], "type": "kelime"})
                node_ids.add(target_id)
            links.append({"source": center_id, "target": target_id, "type": "kelime"})
    except:
        pass
    
    # Get outgoing semantic similarity
    try:
        result = db.execute(text(
            "SELECT target_surah, target_ayat FROM semantic_similarity WHERE source_surah = :s AND source_ayat = :a"
        ), {"s": surah_number, "a": ayat_number})
        for row in result:
            target_id = f"{row[0]}:{row[1]}"
            if target_id not in node_ids:
                nodes.append({"id": target_id, "label": target_id, "surah": row[0], "ayat": row[1], "type": "anlam"})
                node_ids.add(target_id)
            links.append({"source": center_id, "target": target_id, "type": "anlam"})
    except:
        pass
    
    # Get incoming references (others -> this verse)
    try:
        result = db.execute(text(
            "SELECT source_surah, source_ayat FROM similar_ayat WHERE target_surah = :s AND target_ayat = :a"
        ), {"s": surah_number, "a": ayat_number})
        for row in result:
            source_id = f"{row[0]}:{row[1]}"
            if source_id not in node_ids:
                nodes.append({"id": source_id, "label": source_id, "surah": row[0], "ayat": row[1], "type": "ref"})
                node_ids.add(source_id)
            links.append({"source": source_id, "target": center_id, "type": "ref"})
    except:
        pass
    
    try:
        result = db.execute(text(
            "SELECT source_surah, source_ayat FROM semantic_similarity WHERE target_surah = :s AND target_ayat = :a"
        ), {"s": surah_number, "a": ayat_number})
        for row in result:
            source_id = f"{row[0]}:{row[1]}"
            if source_id not in node_ids:
                nodes.append({"id": source_id, "label": source_id, "surah": row[0], "ayat": row[1], "type": "ref"})
                node_ids.add(source_id)
            links.append({"source": source_id, "target": center_id, "type": "ref"})
    except:
        pass
    
    graph_data = json.dumps({"nodes": nodes, "links": links})
    
    return templates.TemplateResponse("verse_graph.html", {
        "request": request,
        "surah_number": surah_number,
        "ayat_number": ayat_number,
        "surah_name": surah_name,
        "graph_data": graph_data
    })
