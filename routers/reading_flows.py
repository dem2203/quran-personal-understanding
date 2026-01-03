from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import ReadingFlow

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/reading-flows", response_class=HTMLResponse)
async def read_reading_flows(request: Request, db: Session = Depends(get_db)):
    flows = db.query(ReadingFlow).all()
    return templates.TemplateResponse("reading_flows.html", {
        "request": request,
        "flows": flows
    })

@router.get("/reading-flow/{flow_id}", response_class=HTMLResponse)
async def read_reading_flow_detail(request: Request, flow_id: int, db: Session = Depends(get_db)):
    flow = db.query(ReadingFlow).filter(ReadingFlow.id == flow_id).first()
    return templates.TemplateResponse("reading_flow_detail.html", {
        "request": request,
        "flow": flow
    })
