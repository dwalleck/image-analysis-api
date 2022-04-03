from typing import List, Mapping
from databases import Database
from sqlalchemy import Table


class ImageRepository:
    def __init__(self, images_table: Table, database: Database) -> None:
        self.images_table = images_table
        self.database = database

    async def get_image(self, image_id: int) -> Mapping | None:
        query = self.images_table.select().where(self.images_table.c.id == image_id)
        image_from_db = await self.database.fetch_one(query)
        return image_from_db

    async def get_images(self, objects: str | None) -> List[Mapping]:
        if objects is None:
            query = self.images_table.select()
        else:
            query = self.images_table.select().where(
                self.images_table.c.objects.contains(objects.split(","))
            )
        images_from_db = await self.database.fetch_all(query)
        return images_from_db

    async def create_image(
        self, label: str, url: str, analyze_image: bool, objects: List[str]
    ) -> int:
        query = self.images_table.insert().values(
            label=label,
            url=url,
            analyze_image=analyze_image,
            objects=objects,
        )

        image_id = await self.database.execute(query)
        return image_id
