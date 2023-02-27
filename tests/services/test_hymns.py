from typing import List

import funml as ml
import pytest
from services import hymns
from services.hymns.errors import NotFoundError, ValidationError
from services.hymns.models import MusicalNote, Song
from services.hymns.types import HymnsService
from services.hymns.utils.shared import note_to_str
from ..conftest import songs_fixture, songs_langs_fixture


@pytest.mark.asyncio
async def test_initialize(service_root_path):
    """initialize initializes the hymns store and everything required"""
    hymns_service = await hymns.initialize(service_root_path)
    assert isinstance(hymns_service, hymns.types.HymnsService)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song", songs_fixture)
async def test_add_song(service: HymnsService, song: Song):
    """add_song adds a given song to the hymns store"""
    await _assert_song_does_not_exist(service, song)

    res = await hymns.add_song(service, song=song)
    assert res == ml.Result.OK(song)

    await _assert_song_exists(service, song)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song", songs_fixture)
async def test_get_song_by_title(service: HymnsService, song: Song):
    """get_song_by_title gets a given song basing on its title"""
    await hymns.add_song(service, song=song)
    res = await hymns.get_song_by_title(
        service, title=song.title, language=song.language
    )
    assert res == ml.Result.OK(song)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song", songs_fixture)
async def test_get_song_by_title_not_found(service: HymnsService, song: Song):
    """get_song_by_title returns Result.ERR if not found"""
    res = await hymns.get_song_by_title(
        service, title=song.title, language=song.language
    )
    err = _extract_exception(res)
    assert isinstance(err, NotFoundError)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song", songs_fixture)
async def test_get_song_by_number(service: HymnsService, song: Song):
    """get_song_by_number gets a given song by the hymn number"""
    await hymns.add_song(service, song=song)
    res = await hymns.get_song_by_number(
        service, number=song.number, language=song.language
    )
    assert res == ml.Result.OK(song)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song", songs_fixture)
async def test_get_song_by_number_not_found(service: HymnsService, song: Song):
    """get_song_by_number returns Result.ERR if not found"""
    res = await hymns.get_song_by_number(
        service, number=song.number, language=song.language
    )
    err = _extract_exception(res)
    assert isinstance(err, NotFoundError)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, languages", songs_langs_fixture)
async def test_delete_song_requires_title_or_number(
    service: HymnsService, song: Song, languages: List[str]
):
    """delete_song requires a number or a title or returns a result with a ValidationError"""
    await hymns.add_song(service, song=song)
    res = await hymns.delete_song(service)
    err = _extract_exception(res)
    assert isinstance(err, ValidationError)
    await _assert_song_exists(service, song)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, languages", songs_langs_fixture)
async def test_delete_song_not_found(
    service: HymnsService, song: Song, languages: List[str]
):
    """delete_song a non existent song returns a result with a NotFoundError"""
    res = await hymns.delete_song(service, title=song.title)
    err = _extract_exception(res)
    assert isinstance(err, NotFoundError)

    res = await hymns.delete_song(service, number=song.number)
    err = _extract_exception(res)
    assert isinstance(err, NotFoundError)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, languages", songs_langs_fixture)
async def test_delete_song_by_title_all_langs(
    service: HymnsService, song: Song, languages: List[str]
):
    """delete_song removes the song of the given title from all languages from the hymns store"""
    song_versions = [
        Song(**{**ml.to_dict(song), "language": lang}) for lang in languages
    ]
    for song_version in song_versions:
        await hymns.add_song(service, song=song_version)

    res = await hymns.delete_song(service, title=song.title)
    assert res == ml.Result.OK(song_versions)

    for song_version in song_versions:
        await _assert_song_does_not_exist(service, song_version)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, languages", songs_langs_fixture)
async def test_delete_song_by_number_all_langs(
    service: HymnsService, song: Song, languages: List[str]
):
    """delete_song removes the song of the given number from all languages from the hymns store"""
    song_versions = [
        Song(**{**ml.to_dict(song), "language": lang}) for lang in languages
    ]

    for song_version in song_versions:
        await hymns.add_song(service, song=song_version)

    res = await hymns.delete_song(service, number=song.number)
    assert res == ml.Result.OK(song_versions)

    for song_version in song_versions:
        await _assert_song_does_not_exist(service, song_version)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, languages", songs_langs_fixture)
async def test_delete_song_by_title_one_lang(
    service: HymnsService, song: Song, languages: List[str]
):
    """delete_song removes the song of the given title from one language from the hymns store"""
    song_versions = {
        lang: Song(**{**ml.to_dict(song), "language": lang}) for lang in languages
    }
    for song_version in song_versions.values():
        await hymns.add_song(service, song=song_version)

    for lang in languages:
        await _assert_song_exists(service, song_versions[lang])

        res = await hymns.delete_song(service, title=song.title, language=lang)
        assert res == ml.Result.OK([song_versions[lang]])

        await _assert_song_does_not_exist(service, song_versions[lang])


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, languages", songs_langs_fixture)
async def test_delete_song_by_number_one_lang(
    service: HymnsService, song: Song, languages: List[str]
):
    """delete_song removes the song of the given number from one language from the hymns store"""
    song_versions = {
        lang: Song(**{**ml.to_dict(song), "language": lang}) for lang in languages
    }
    for song_version in song_versions.values():
        await hymns.add_song(service, song=song_version)

    for lang in languages:
        await _assert_song_exists(service, song_versions[lang])

        res = await hymns.delete_song(service, number=song.number, language=lang)
        assert res == ml.Result.OK([song_versions[lang]])

        await _assert_song_does_not_exist(service, song_versions[lang])


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


async def _assert_song_exists(service, song):
    """Asserts that the song exists in the service"""
    res = await hymns.get_song_by_title(
        service, title=song.title, language=song.language
    )
    assert res == ml.Result.OK(song)


async def _assert_song_does_not_exist(service, song):
    """Asserts that the song does not exist in the service"""
    res = await hymns.get_song_by_title(
        service, title=song.title, language=song.language
    )
    err = _extract_exception(res)
    assert isinstance(err, NotFoundError)


def _extract_exception(res: ml.Result) -> Exception:
    """Extracts the exception within the result"""
    return (
        ml.match()
        .case(ml.Result.ERR(Exception), do=lambda v: v)
        .case(ml.Result.OK, do=lambda: None)(res)
    )
