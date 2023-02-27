import funml as ml
import pytest
from services import hymns
from services.hymns.models import MusicalNote, Song
from services.hymns.types import HymnsService
from services.hymns.utils.shared import note_to_str
from ..conftest import songs_fixture


@pytest.mark.asyncio
async def test_initialize(service_root_path):
    """initialize initializes the hymns store and everything required"""
    hymns_service = await hymns.initialize(service_root_path)
    assert isinstance(hymns_service, hymns.types.HymnsService)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song", songs_fixture)
async def test_add_song(service: HymnsService, song: Song):
    """add_song adds a given song to the hymns store"""
    res = await hymns.add_song(service, song=song)
    assert res == ml.Result.OK(song)


@pytest.mark.asyncio
async def test_delete_song():
    """delete_song removes a song from the hymns store"""
    pass


@pytest.mark.asyncio
async def test_get_song_by_title():
    """get_song_by_title gets a given song basing on its title"""
    pass


@pytest.mark.asyncio
async def test_get_song_by_number():
    """get_song_by_number gets a given song by the hymn number"""
    pass


@pytest.mark.asyncio
async def test_query_song_by_title():
    """query_song_by_title queries for songs whose title start with a given phrase"""
    pass


@pytest.mark.asyncio
async def test_query_song_by_number():
    """query_song_by_title queries for songs whose song number start with a given set of digits"""
    pass


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
