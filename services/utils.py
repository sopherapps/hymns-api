"""Contains the utility functions shared across services"""
from __future__ import annotations

import json
from os import path

import funml as ml


from os import PathLike

from funml import to_dict

from services.hymns.models import MusicalNote


def get_store_path(root_path: bytes | PathLike[bytes] | str, name: str) -> str:
    """Gets the path to the store given a root path"""
    return path.join(root_path, name)


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


def record_to_json(value: ml.Record) -> str:
    """Converts an ml record to a JSON string.

    Args:
        value: the record to convert to a JSON string

    Returns:
        the record as a JSON string
    """
    return json.dumps(to_dict(value))
