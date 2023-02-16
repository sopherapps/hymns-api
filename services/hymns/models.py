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
