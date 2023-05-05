from enum import Enum
from typing import Dict


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

    @classmethod
    def set(cls) -> Dict[str, str]:
        """Returns the complete set of the members as a map"""
        return {
            _normalize_musical_note_name(name): cls.__members__[name].value
            for name in cls.__members__
        }


def _normalize_musical_note_name(note_name: str) -> str:
    """Converts the name of the musical note name to a human-friendly alternative"""
    return note_name.replace("_", " ").replace(" SHARP", "#").capitalize()
