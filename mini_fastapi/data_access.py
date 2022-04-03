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
    Column("url", String),
    Column("analyze_image", Boolean),
    Column("objects", ARRAY(String)),
)

engine = create_engine(DATABASE_URL)

metadata.create_all(engine)


# TODO Remove these functions
def get_image_by_id(image_id: int) -> List[dict]:
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
