from sqlalchemy.orm import Session
from . import models, schemas

def get_url(db: Session, url_id: int):
    return db.query(models.URL).filter(models.URL.id == url_id).first()

def get_urls(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.URL).offset(skip).limit(limit).all()

def create_url(db: Session, url: schemas.URLCreate):
    db_url = models.URL(**url.dict())
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def delete_url(db: Session, url_id: int):
    db_url = db.query(models.URL).filter(models.URL.id == url_id).first()
    if db_url:
        db.delete(db_url)
        db.commit()
    return db_url