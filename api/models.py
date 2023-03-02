from enum import Enum
from typing import List, Optional, Dict
from services.hymns import models as hymns
import funml as ml

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

    def to_hymns_musical_note(self) -> hymns.MusicalNote:
        """Returns the hymns.models.MusicalNote equivalent of the current instance"""
        return (
            ml.match()
            .case(MusicalNote.C_MAJOR, do=ml.val(hymns.MusicalNote.C_MAJOR))
            .case(MusicalNote.C_MINOR, do=ml.val(hymns.MusicalNote.C_MINOR))
            .case(
                MusicalNote.C_SHARP_MAJOR,
                do=ml.val(hymns.MusicalNote.C_SHARP_MAJOR),
            )
            .case(
                MusicalNote.C_SHARP_MINOR,
                do=ml.val(hymns.MusicalNote.C_SHARP_MINOR),
            )
            .case(MusicalNote.D_MAJOR, do=ml.val(hymns.MusicalNote.D_MAJOR))
            .case(MusicalNote.D_MINOR, do=ml.val(hymns.MusicalNote.D_MINOR))
            .case(
                MusicalNote.D_SHARP_MAJOR,
                do=ml.val(hymns.MusicalNote.D_SHARP_MAJOR),
            )
            .case(
                MusicalNote.D_SHARP_MINOR,
                do=ml.val(hymns.MusicalNote.D_SHARP_MINOR),
            )
            .case(MusicalNote.E_MAJOR, do=ml.val(hymns.MusicalNote.E_MAJOR))
            .case(MusicalNote.E_MINOR, do=ml.val(hymns.MusicalNote.E_MINOR))
            .case(MusicalNote.F_MAJOR, do=ml.val(hymns.MusicalNote.F_MAJOR))
            .case(MusicalNote.F_MINOR, do=ml.val(hymns.MusicalNote.F_MINOR))
            .case(
                MusicalNote.F_SHARP_MAJOR,
                do=ml.val(hymns.MusicalNote.F_SHARP_MAJOR),
            )
            .case(
                MusicalNote.F_SHARP_MINOR,
                do=ml.val(hymns.MusicalNote.F_SHARP_MINOR),
            )
            .case(MusicalNote.G_MAJOR, do=ml.val(hymns.MusicalNote.G_MAJOR))
            .case(MusicalNote.G_MINOR, do=ml.val(hymns.MusicalNote.G_MINOR))
            .case(
                MusicalNote.G_SHARP_MAJOR,
                do=ml.val(hymns.MusicalNote.G_SHARP_MAJOR),
            )
            .case(
                MusicalNote.G_SHARP_MINOR,
                do=ml.val(hymns.MusicalNote.G_SHARP_MINOR),
            )
            .case(MusicalNote.A_MAJOR, do=ml.val(hymns.MusicalNote.A_MAJOR))
            .case(MusicalNote.A_MINOR, do=ml.val(hymns.MusicalNote.A_MINOR))
            .case(
                MusicalNote.A_SHARP_MAJOR,
                do=ml.val(hymns.MusicalNote.A_SHARP_MAJOR),
            )
            .case(
                MusicalNote.A_SHARP_MINOR,
                do=ml.val(hymns.MusicalNote.A_SHARP_MINOR),
            )
            .case(MusicalNote.B_MAJOR, do=ml.val(hymns.MusicalNote.B_MAJOR))
            .case(MusicalNote.B_MINOR, do=ml.val(hymns.MusicalNote.B_MINOR))(self)
        )

    @classmethod
    def from_hymns_musical_note(cls, note: hymns.MusicalNote) -> "MusicalNote":
        """Returns the MusicalNote equivalent of the hymns.models.MusicalNote"""
        return (
            ml.match()
            .case(hymns.MusicalNote.C_MAJOR, do=ml.val(MusicalNote.C_MAJOR))
            .case(hymns.MusicalNote.C_MINOR, do=ml.val(MusicalNote.C_MINOR))
            .case(
                hymns.MusicalNote.C_SHARP_MAJOR,
                do=ml.val(MusicalNote.C_SHARP_MAJOR),
            )
            .case(
                hymns.MusicalNote.C_SHARP_MINOR,
                do=ml.val(MusicalNote.C_SHARP_MINOR),
            )
            .case(hymns.MusicalNote.D_MAJOR, do=ml.val(MusicalNote.D_MAJOR))
            .case(hymns.MusicalNote.D_MINOR, do=ml.val(MusicalNote.D_MINOR))
            .case(
                hymns.MusicalNote.D_SHARP_MAJOR,
                do=ml.val(MusicalNote.D_SHARP_MAJOR),
            )
            .case(
                hymns.MusicalNote.D_SHARP_MINOR,
                do=ml.val(MusicalNote.D_SHARP_MINOR),
            )
            .case(hymns.MusicalNote.E_MAJOR, do=ml.val(MusicalNote.E_MAJOR))
            .case(hymns.MusicalNote.E_MINOR, do=ml.val(MusicalNote.E_MINOR))
            .case(hymns.MusicalNote.F_MAJOR, do=ml.val(MusicalNote.F_MAJOR))
            .case(hymns.MusicalNote.F_MINOR, do=ml.val(MusicalNote.F_MINOR))
            .case(
                hymns.MusicalNote.F_SHARP_MAJOR,
                do=ml.val(MusicalNote.F_SHARP_MAJOR),
            )
            .case(
                hymns.MusicalNote.F_SHARP_MINOR,
                do=ml.val(MusicalNote.F_SHARP_MINOR),
            )
            .case(hymns.MusicalNote.G_MAJOR, do=ml.val(MusicalNote.G_MAJOR))
            .case(hymns.MusicalNote.G_MINOR, do=ml.val(MusicalNote.G_MINOR))
            .case(
                hymns.MusicalNote.G_SHARP_MAJOR,
                do=ml.val(MusicalNote.G_SHARP_MAJOR),
            )
            .case(
                hymns.MusicalNote.G_SHARP_MINOR,
                do=ml.val(MusicalNote.G_SHARP_MINOR),
            )
            .case(hymns.MusicalNote.A_MAJOR, do=ml.val(MusicalNote.A_MAJOR))
            .case(hymns.MusicalNote.A_MINOR, do=ml.val(MusicalNote.A_MINOR))
            .case(
                hymns.MusicalNote.A_SHARP_MAJOR,
                do=ml.val(MusicalNote.A_SHARP_MAJOR),
            )
            .case(
                hymns.MusicalNote.A_SHARP_MINOR,
                do=ml.val(MusicalNote.A_SHARP_MINOR),
            )
            .case(hymns.MusicalNote.B_MAJOR, do=ml.val(MusicalNote.B_MAJOR))
            .case(hymns.MusicalNote.B_MINOR, do=ml.val(MusicalNote.B_MINOR))(note)
        )


class LineSection(BaseModel):
    note: MusicalNote
    words: str

    def to_hymns_line_section(self) -> hymns.LineSection:
        """Returns the hymns.models.LineSection equivalent of current instance"""
        return hymns.LineSection(
            note=self.note.to_hymns_musical_note(), words=self.words
        )

    @classmethod
    def from_hymns_line_section(cls, section: hymns.LineSection) -> "LineSection":
        """Returns the LineSection equivalent of the hymns.models.LineSection passed"""
        return LineSection(
            note=MusicalNote.from_hymns_musical_note(section.note), words=section.words
        )


class Song(BaseModel):
    number: int
    language: str
    title: str
    key: MusicalNote
    lines: List[List[LineSection]]

    def to_hymns_song(self) -> hymns.Song:
        """Returns the hymns.models.Song equivalent of current instance"""
        return hymns.Song(
            number=self.number,
            language=self.language,
            title=self.title,
            key=self.key.to_hymns_musical_note(),
            lines=[
                [section.to_hymns_line_section() for section in line]
                for line in self.lines
            ],
        )

    @classmethod
    def from_hymns_song(cls, song: hymns.Song) -> "Song":
        """Returns the Song equivalent of the hymns.models.Song passed to it"""
        return cls(
            number=song.number,
            language=song.language,
            title=song.title,
            key=MusicalNote.from_hymns_musical_note(song.key),
            lines=[
                [LineSection.from_hymns_line_section(section) for section in line]
                for line in song.lines
            ],
        )


class PartialSong(BaseModel):
    number: Optional[int]
    language: Optional[str]
    title: Optional[str]
    key: Optional[MusicalNote]
    lines: Optional[List[List[LineSection]]]


class SongDetail(BaseModel):
    number: int
    translations: Dict[str, Song]


class PaginatedResponse(BaseModel):
    """A response that is returned when paginated"""

    skip: int = 0
    limit: int = 0
    data: List[SongDetail] = []
