"""Contains the models for the hymns service
"""
from typing import List, Callable
import funml as ml

from pydantic import BaseModel


"""
Data Types
"""


@ml.record
class Song(BaseModel):
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
class LineSection(BaseModel):
    note: MusicalNote
    words: str


"""
Main Expressions
"""
note_to_str: Callable[["MusicalNote"], str] = (
    ml.match()
    .case(MusicalNote.C_MAJOR, do=ml.val("C"))
    .case(MusicalNote.C_MINOR, do=ml.val("Cm"))
    .case(MusicalNote.C_SHARP_MAJOR, do=ml.val("C#"))
    .case(MusicalNote.C_SHARP_MINOR, do=ml.val("C#m"))
    .case(MusicalNote.D_MAJOR, do=ml.val("D"))
    .case(MusicalNote.D_SHARP_MAJOR, do=ml.val("D#"))
    .case(MusicalNote.D_SHARP_MINOR, do=ml.val("D#m"))
    .case(MusicalNote.E_MAJOR, do=ml.val("E"))
    .case(MusicalNote.E_MINOR, do=ml.val("Em"))
    .case(MusicalNote.F_MAJOR, do=ml.val("F"))
    .case(MusicalNote.F_MINOR, do=ml.val("Fm"))
    .case(MusicalNote.F_SHARP_MAJOR, do=ml.val("F#"))
    .case(MusicalNote.F_SHARP_MINOR, do=ml.val("F#m"))
    .case(MusicalNote.G_MAJOR, do=ml.val("G"))
    .case(MusicalNote.G_MINOR, do=ml.val("Gm"))
    .case(MusicalNote.G_SHARP_MAJOR, do=ml.val("G#"))
    .case(MusicalNote.G_SHARP_MINOR, do=ml.val("G#m"))
    .case(MusicalNote.A_MAJOR, do=ml.val("A"))
    .case(MusicalNote.A_MINOR, do=ml.val("Am"))
    .case(MusicalNote.A_SHARP_MAJOR, do=ml.val("A#"))
    .case(MusicalNote.A_SHARP_MINOR, do=ml.val("A#m"))
    .case(MusicalNote.B_MAJOR, do=ml.val("B"))
    .case(MusicalNote.B_MINOR, do=ml.val("Bm"))
)
"""Converts a MusicalNote to a string"""
