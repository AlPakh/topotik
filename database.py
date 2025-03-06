import os
import uuid
from sqlalchemy import (
    create_engine, Column, String, Text, Enum, ForeignKey, DateTime,
    Integer, DECIMAL, Table, text
)
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

# ------------------------------------------------------------------------------
#  Шаг 1: Подключаемся к базе (как и в вашем коде database.py).
# ------------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не установлен в переменных окружения!")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------------------------------------------------------------------
#  Шаг 2: Определяем перечисления (Enum) для удобства
# ------------------------------------------------------------------------------
MapTypeEnum = Enum('osm', 'custom_image', name='map_type_enum', create_type=False)
AccessLevelEnum = Enum('private', 'link', 'public', name='access_level_enum', create_type=False)
BlockTypeEnum = Enum('text', 'image', 'video', 'link', name='block_type_enum', create_type=False)
ResourceTypeEnum = Enum('map', 'collection', name='resource_type_enum', create_type=False)
PermissionLevelEnum = Enum('view', 'edit', name='permission_level_enum', create_type=False)

# ------------------------------------------------------------------------------
#  Шаг 3: Определяем модели (таблицы)
# ------------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    # UUID в качестве первичного ключа. default=uuid.uuid4 генерирует в Python
    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь: один пользователь -> многие карты, коллекции, изображения и т.п.
    maps = relationship("Map", back_populates="owner")  
    collections = relationship("Collection", back_populates="owner")
    images = relationship("Image", back_populates="owner")

class Map(Base):
    __tablename__ = "maps"

    map_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    title = Column(String(100), nullable=False)
    map_type = Column(MapTypeEnum, nullable=False)  # 'osm' или 'custom_image'
    image_url = Column(Text)                        # может быть URL, если custom_image
    access_level = Column(AccessLevelEnum, nullable=False, default="private")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="maps")
    markers = relationship("Marker", back_populates="map", cascade="all, delete-orphan")
    collections = relationship("Collection", back_populates="map", cascade="all, delete-orphan")

class Collection(Base):
    __tablename__ = "collections"

    collection_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    map_id = Column(UUID(as_uuid=True), ForeignKey("maps.map_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    title = Column(String(100), nullable=False)
    access_level = Column(AccessLevelEnum, nullable=False, default="private")

    map = relationship("Map", back_populates="collections")
    owner = relationship("User", back_populates="collections")

    # Связь (M:M) через вспомогательную таблицу markers_collections
    markers = relationship("Marker",
                           secondary="markers_collections",
                           back_populates="collections")

class Marker(Base):
    __tablename__ = "markers"

    marker_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    map_id = Column(UUID(as_uuid=True), ForeignKey("maps.map_id"), nullable=False)
    latitude = Column(DECIMAL(9,6), nullable=False)
    longitude = Column(DECIMAL(9,6), nullable=False)
    title = Column(String(100))
    description = Column(Text)

    map = relationship("Map", back_populates="markers")
    collections = relationship("Collection",
                               secondary="markers_collections",
                               back_populates="markers")
    articles = relationship("Article", back_populates="marker", cascade="all, delete-orphan")

# Вспомогательная таблица для связи M:M между метками (Markers) и коллекциями (Collections).
markers_collections_table = Table(
    "markers_collections",
    Base.metadata,
    Column("marker_id", UUID(as_uuid=True), ForeignKey("markers.marker_id"), primary_key=True),
    Column("collection_id", UUID(as_uuid=True), ForeignKey("collections.collection_id"), primary_key=True)
)

class Article(Base):
    __tablename__ = "articles"

    article_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    marker_id = Column(UUID(as_uuid=True), ForeignKey("markers.marker_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    marker = relationship("Marker", back_populates="articles")
    blocks = relationship("Block", back_populates="article", cascade="all, delete-orphan")

class Block(Base):
    __tablename__ = "blocks"

    block_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.article_id"), nullable=False)
    type = Column(BlockTypeEnum, nullable=False)  # 'text', 'image', 'video', 'link'
    content = Column(Text)                        # либо JSONB, если нужно хранить структуру
    order = Column(Integer)

    article = relationship("Article", back_populates="blocks")

class Sharing(Base):
    __tablename__ = "sharing"

    sharing_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    resource_type = Column(ResourceTypeEnum, nullable=False)  # 'map' или 'collection'
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    access_token = Column(String(255))
    access_level = Column(PermissionLevelEnum, nullable=False, default="view")

    # user_id может быть NULL, если доступ "публичный" (public) или доступ "по ссылке" (link).
    user = relationship("User", foreign_keys=[user_id])

class Image(Base):
    __tablename__ = "images"

    image_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer)
    data = Column(BYTEA, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="images")

# ------------------------------------------------------------------------------
#  Шаг 4: Создаем таблицы в базе
# ------------------------------------------------------------------------------
def init_db():
    # При первом запуске создадим перечислимые типы (Enum), если их нет.
    # create_type=False в Enum говорит, что тип может быть не создан автоматически.
    # Чтобы корректно создать типы, можно выполнить:
    MapTypeEnum.create(engine, checkfirst=True)
    AccessLevelEnum.create(engine, checkfirst=True)
    BlockTypeEnum.create(engine, checkfirst=True)
    ResourceTypeEnum.create(engine, checkfirst=True)
    PermissionLevelEnum.create(engine, checkfirst=True)

    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("All tables created successfully!")
