"""Utilities common to many operations"""
from typing import TYPE_CHECKING

import funml as ml

from services.hymns.errors import NotFoundError
from services.hymns.models import MusicalNote

if TYPE_CHECKING:
    from ..types import HymnsService


def get_language_store(service: "HymnsService", lang: str):
    """Gets the language store for the given language from the service

    Args:
        service: the HymnsService from which the language store is to be got
        lang: the language of the store to be got

    Raises:
        NotFoundError: no such language found
    """
    try:
        return service.stores[lang]
    except KeyError:
        raise NotFoundError(f"no such language as {lang}")


def note_to_str(note: MusicalNote) -> str:
    """Converts a MusicalNote to a string"""
    return (
        ml.match(note)
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
    )()
