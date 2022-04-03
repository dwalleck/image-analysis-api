from typing import List
import uuid

import databases
from sqlalchemy import (
    Table,
    Column,
    Boolean,
    MetaData,
    String,
    Integer,
    create_engine,
)
from sqlalchemy.dialects.postgresql import ARRAY


DATABASE_URL = "postgresql://images_user:password@localhost:5432/image_analysis"

database = databases.Database(DATABASE_URL)

metadata = MetaData()

images: Table = Table(
    "images",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("label", String(50), nullable=False),
    Column("image_blob_name", String),
    Column("analyze_image", Boolean),
    Column("tags", ARRAY(String), nullable=True),
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
