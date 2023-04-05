"""Contains the models for the hymns service
"""
from typing import List, Optional
from pydantic import BaseModel

from services.types import MusicalNote


class LineSection(BaseModel):
    note: MusicalNote
    words: str


class Song(BaseModel):
    number: int
    language: str
    title: str
    key: MusicalNote
    lines: List[List[LineSection]]


class PaginatedResponse(BaseModel):
    """A response that is returned when paginated"""

    skip: Optional[int] = None
    limit: Optional[int] = None
    data: list[Song] = []
