from typing import List

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

from mini_fastapi.api.config import get_config

config = get_config()
database = databases.Database(config.postgres_connection_string)
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

engine = create_engine(config.postgres_connection_string)
metadata.create_all(engine)
