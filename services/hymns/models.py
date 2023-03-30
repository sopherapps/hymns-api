"""Contains the models for the hymns service
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class MusicalNote(str, Enum):
    C_MAJOR = "C"
    C_MINOR = "Cm"
    C_SHARP_MAJOR = "C#"
    C_SHARP_MINOR = "C#m"
    D_MAJOR = "D"
    D_MINOR = "Dm"
    D_SHARP_MAJOR = "D#"
    D_SHARP_MINOR = "D#m"
    E_MAJOR = "E"
    E_MINOR = "Em"
    F_MAJOR = "F"
    F_MINOR = "Fm"
    F_SHARP_MAJOR = "F#"
    F_SHARP_MINOR = "F#m"
    G_MAJOR = "G"
    G_MINOR = "Gm"
    G_SHARP_MAJOR = "G#"
    G_SHARP_MINOR = "G#m"
    A_MAJOR = "A"
    A_MINOR = "Am"
    A_SHARP_MAJOR = "A#"
    A_SHARP_MINOR = "A#m"
    B_MAJOR = "B"
    B_MINOR = "Bm"


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
