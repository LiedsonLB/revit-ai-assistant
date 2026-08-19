from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Requirement
from ..schemas import RequirementOut

router = APIRouter(prefix="/requirements", tags=["requirements"])


@router.get("", response_model=list[RequirementOut])
def list_requirements(db: Session = Depends(get_db)):
    return db.query(Requirement).order_by(Requirement.environment).all()


@router.get("/{environment}", response_model=RequirementOut)
def get_requirement(environment: str, db: Session = Depends(get_db)):
    req = db.query(Requirement).filter(Requirement.environment.ilike(environment)).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requisito não encontrado")
    return req
