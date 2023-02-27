"""Contains the models for the hymns service
"""
from __future__ import annotations
from typing import List
import funml as ml


@ml.record
class Song:
    number: int
    language: str
    title: str
    key: "MusicalNote"
    lines: List[List["LineSection"]]


class MusicalNote(ml.Enum):
    C_MAJOR = None
    C_MINOR = None
    C_SHARP_MAJOR = None
    C_SHARP_MINOR = None
    D_MAJOR = None
    D_MINOR = None
    D_SHARP_MAJOR = None
    D_SHARP_MINOR = None
    E_MAJOR = None
    E_MINOR = None
    F_MAJOR = None
    F_MINOR = None
    F_SHARP_MAJOR = None
    F_SHARP_MINOR = None
    G_MAJOR = None
    G_MINOR = None
    G_SHARP_MAJOR = None
    G_SHARP_MINOR = None
    A_MAJOR = None
    A_MINOR = None
    A_SHARP_MAJOR = None
    A_SHARP_MINOR = None
    B_MAJOR = None
    B_MINOR = None


@ml.record
class LineSection:
    note: MusicalNote
    words: str


@ml.record
class PaginatedResponse:
    """A response that is returned when paginated"""

    skip: int | None = None
    limit: int | None = None
    data: list[Song] = []
