from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from uuid import UUID
from jose import jwt
from app import models, schemas, config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = config.settings.SECRET_KEY
ALGORITHM  = config.settings.ALGORITHM
EXPIRE_MIN = config.settings.ACCESS_TOKEN_EXPIRE_MINUTES

# ————————————————————————————————————————————————
# User & Auth (как было выше)
# ————————————————————————————————————————————————

# ————————————————————————————————————————————————
# Maps (как было выше)
# ————————————————————————————————————————————————

# ————————————————————————————————————————————————
# Collections
def get_collection(db: Session, collection_id: UUID):
    return db.query(models.Collection).filter(models.Collection.collection_id == collection_id).first()

def get_collections(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Collection).offset(skip).limit(limit).all()

def create_collection(db: Session, collection_in: schemas.CollectionCreate, user_id: UUID):
    db_coll = models.Collection(**collection_in.dict(), user_id=user_id)
    db.add(db_coll)
    db.commit()
    db.refresh(db_coll)
    return db_coll

def update_collection(db: Session, collection_id: UUID, data: dict):
    coll = get_collection(db, collection_id)
    for key, val in data.items():
        setattr(coll, key, val)
    db.commit()
    db.refresh(coll)
    return coll

def delete_collection(db: Session, collection_id: UUID):
    coll = get_collection(db, collection_id)
    db.delete(coll)
    db.commit()
    return coll

# ————————————————————————————————————————————————
# Markers
def get_marker(db: Session, marker_id: UUID):
    return db.query(models.Marker).filter(models.Marker.marker_id == marker_id).first()

def get_markers_by_map(db: Session, map_id: UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Marker)
          .filter(models.Marker.map_id == map_id)
          .offset(skip)
          .limit(limit)
          .all()
    )

def create_marker(db: Session, marker_in: schemas.MarkerCreate):
    db_marker = models.Marker(**marker_in.dict())
    db.add(db_marker)
    db.commit()
    db.refresh(db_marker)
    return db_marker

def update_marker(db: Session, marker_id: UUID, data: dict):
    m = get_marker(db, marker_id)
    for key, val in data.items():
        setattr(m, key, val)
    db.commit()
    db.refresh(m)
    return m

def delete_marker(db: Session, marker_id: UUID):
    m = get_marker(db, marker_id)
    db.delete(m)
    db.commit()
    return m

# ————————————————————————————————————————————————
# Articles
def get_article(db: Session, article_id: UUID):
    return db.query(models.Article).filter(models.Article.article_id == article_id).first()

def get_articles_by_marker(db: Session, marker_id: UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Article)
          .filter(models.Article.marker_id == marker_id)
          .offset(skip)
          .limit(limit)
          .all()
    )

def create_article(db: Session, article_in: schemas.ArticleCreate):
    db_art = models.Article(**article_in.dict())
    db.add(db_art)
    db.commit()
    db.refresh(db_art)
    return db_art

def delete_article(db: Session, article_id: UUID):
    art = get_article(db, article_id)
    db.delete(art)
    db.commit()
    return art

# ————————————————————————————————————————————————
# Blocks
def get_block(db: Session, block_id: UUID):
    return db.query(models.Block).filter(models.Block.block_id == block_id).first()

def get_blocks_by_article(db: Session, article_id: UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Block)
          .filter(models.Block.article_id == article_id)
          .offset(skip)
          .limit(limit)
          .all()
    )

def create_block(db: Session, block_in: schemas.BlockCreate):
    db_blk = models.Block(**block_in.dict())
    db.add(db_blk)
    db.commit()
    db.refresh(db_blk)
    return db_blk

def update_block(db: Session, block_id: UUID, data: dict):
    blk = get_block(db, block_id)
    for key, val in data.items():
        setattr(blk, key, val)
    db.commit()
    db.refresh(blk)
    return blk

def delete_block(db: Session, block_id: UUID):
    blk = get_block(db, block_id)
    db.delete(blk)
    db.commit()
    return blk
