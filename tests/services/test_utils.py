"""Tests for all utility functions common across services"""
import json
import os

import funml as ml

from services.hymns.models import MusicalNote
from services.utils import get_store_path, record_to_json, note_to_str

_ROOT_FOLDER_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def test_get_store_path():
    """Returns the path to the store given root path"""
    test_data = {
        "languages": os.path.join(_ROOT_FOLDER_PATH, "languages"),
        "hymns": os.path.join(_ROOT_FOLDER_PATH, "hymns"),
        "auth": os.path.join(_ROOT_FOLDER_PATH, "auth"),
    }

    for k, v in test_data.items():
        assert get_store_path(_ROOT_FOLDER_PATH, k) == v


def test_record_to_json():
    """record_to_json converts a record to JSON string"""

    @ml.record
    class Color:
        r: int
        g: int
        b: int

    test_data = [
        (Color(r=9, g=90, b=7), json.dumps({"r": 9, "g": 90, "b": 7})),
        (Color(r=19, g=100, b=17), json.dumps({"r": 19, "g": 100, "b": 17})),
        (Color(r=4, g=30, b=45), json.dumps({"r": 4, "g": 30, "b": 45})),
    ]

    for item, expected in test_data:
        assert record_to_json(item) == expected


def test_note_to_str():
    """note_to_str converts a MusicalNote into a string"""
    test_data = [
        (MusicalNote.C_MAJOR, "C"),
        (MusicalNote.C_MINOR, "Cm"),
        (MusicalNote.C_SHARP_MAJOR, "C#"),
        (MusicalNote.C_SHARP_MINOR, "C#m"),
        (MusicalNote.D_MAJOR, "D"),
        (MusicalNote.D_SHARP_MAJOR, "D#"),
        (MusicalNote.D_SHARP_MINOR, "D#m"),
        (MusicalNote.E_MAJOR, "E"),
        (MusicalNote.E_MINOR, "Em"),
        (MusicalNote.F_MAJOR, "F"),
        (MusicalNote.F_MINOR, "Fm"),
        (MusicalNote.F_SHARP_MAJOR, "F#"),
        (MusicalNote.F_SHARP_MINOR, "F#m"),
        (MusicalNote.G_MAJOR, "G"),
        (MusicalNote.G_MINOR, "Gm"),
        (MusicalNote.G_SHARP_MAJOR, "G#"),
        (MusicalNote.G_SHARP_MINOR, "G#m"),
        (MusicalNote.A_MAJOR, "A"),
        (MusicalNote.A_MINOR, "Am"),
        (MusicalNote.A_SHARP_MAJOR, "A#"),
        (MusicalNote.A_SHARP_MINOR, "A#m"),
        (MusicalNote.B_MAJOR, "B"),
        (MusicalNote.B_MINOR, "Bm"),
    ]

    for item, expected in test_data:
        assert note_to_str(item) == expected
