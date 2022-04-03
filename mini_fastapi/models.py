import binascii
from typing import List
from pydantic import BaseModel

# # https://github.com/samuelcolvin/pydantic/issues/703#issuecomment-516950935
# class ByteA:
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not isinstance(v, bytes):
#             raise ValueError(f"`bytes` expected not {type(v)}")
#         return binascii.b2a_hex(v)


class AnalyzedImage(BaseModel):
    id: int
    tags: List[str]
    label: str | None = None
    image_data: str

    class Config:
        orm_mode = True
