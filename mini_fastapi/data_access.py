from typing import List
import uuid

import sqlalchemy.dialects.postgresql

import databases
from sqlalchemy import (
    LargeBinary,
    Table,
    Column,
    Boolean,
    MetaData,
    String,
    Integer,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, BYTEA


DATABASE_URL = "postgresql://images_user:password@localhost:5432/image_analysis"

database = databases.Database(DATABASE_URL)

metadata = MetaData()

images: Table = Table(
    "images",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("label", String, nullable=True),
    Column("image_url", String, nullable=True),
    Column("object_detection_enabled", Boolean),
    Column("tags", ARRAY(String), nullable=True),
    Column("image_data", BYTEA),
)

engine = create_engine(DATABASE_URL)

metadata.create_all(engine)


def get_image_by_id(image_id: uuid.UUID) -> List[dict]:
    with database.transaction():
        result = database.fetch_all(
            "SELECT * FROM images WHERE id = $1",
            [image_id],
        )
    return result


def get_image_by_tags(tags: List[str]) -> List[dict]:
    with database.transaction():
        result = database.fetch_all(
            "SELECT * FROM images WHERE tags && $1",
            [tags],
        )
    return result
