from typing import List, Optional, Dict

from pydantic import BaseModel

from services.hymns.models import LineSection, Song, MusicalNote


class PartialSong(BaseModel):
    key: Optional[MusicalNote]
    lines: Optional[List[List[LineSection]]]


class SongDetail(BaseModel):
    number: int
    translations: Dict[str, Song]


class OTPRequest(BaseModel):
    """The One time password request sent to verify a login"""

    otp: str
