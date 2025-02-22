from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..dependencies import get_db

router = APIRouter()

@router.get("/urls", response_model=list[schemas.URL])
def read_urls(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    urls = crud.get_urls(db, skip=skip, limit=limit)
    return urls

@router.post("/urls", response_model=schemas.URL)
def create_url(url: schemas.URLCreate, db: Session = Depends(get_db)):
    return crud.create_url(db=db, url=url)

@router.delete("/urls/{url_id}", response_model=schemas.URL)
def delete_url(url_id: int, db: Session = Depends(get_db)):
    db_url = crud.get_url(db, url_id=url_id)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return crud.delete_url(db=db, url_id=url_id)