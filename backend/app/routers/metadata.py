from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..dependencies import get_db

router = APIRouter()

@router.get("/metadata/{url_id}", response_model=schemas.URL)
def read_metadata(url_id: int, db: Session = Depends(get_db)):
    db_url = crud.get_url(db, url_id=url_id)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return db_url