from typing import List

import funml as ml
import pytest
from services import hymns
from services.hymns.errors import ValidationError
from services.errors import NotFoundError
from services.hymns.models import Song, LineSection, PaginatedResponse
from services.types import MusicalNote
from services.hymns.types import HymnsService
from .conftest import (
    songs_fixture,
    songs_langs_fixture,
    languages,
    service_db_path_fixture,
    hymns_service_fixture,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("service_db_uri", service_db_path_fixture)
async def test_initialize(service_db_uri):
    """initialize initializes the hymns store and everything required"""
    hymns_service = await hymns.initialize(service_db_uri)
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
@pytest.mark.parametrize("service", hymns_service_fixture)
async def test_query_song_by_title(service: HymnsService):
    """query_song_by_title queries for songs whose title start with a given phrase"""
    song_data = dict(
        key=MusicalNote.F_MAJOR,
        lines=[[LineSection(note=MusicalNote.F_MAJOR, words="hey you")]],
    )
    nums_and_titles = [
        (1, "foo"),
        (2, "food"),
        (3, "fell"),
        (4, "fish"),
        (5, "yell"),
        (6, "yearn"),
        (7, "yeast"),
        (8, "yogurt"),
    ]

    test_data = [
        ("f", 0, 0, [(1, "foo"), (2, "food"), (3, "fell"), (4, "fish")]),
        ("f", 1, 0, [(2, "food"), (3, "fell"), (4, "fish")]),
        ("f", 2, 0, [(3, "fell"), (4, "fish")]),
        ("fo", 0, 0, [(1, "foo"), (2, "food")]),
        ("foo", 0, 0, [(1, "foo"), (2, "food")]),
        ("foo", 0, 1, [(1, "foo")]),
        ("fe", 0, 0, [(3, "fell")]),
        ("fi", 0, 0, [(4, "fish")]),
        ("y", 0, 0, [(5, "yell"), (6, "yearn"), (7, "yeast"), (8, "yogurt")]),
        ("ye", 0, 0, [(5, "yell"), (6, "yearn"), (7, "yeast")]),
        ("ye", 1, 2, [(6, "yearn"), (7, "yeast")]),
        ("ye", 1, 1, [(6, "yearn")]),
        ("yea", 0, 0, [(6, "yearn"), (7, "yeast")]),
        ("yo", 0, 0, [(8, "yogurt")]),
    ]

    for lang in languages:
        for num, title in nums_and_titles:
            song = Song(**song_data, title=title, number=num, language=lang)
            await hymns.add_song(service, song=song)

    for lang in languages:
        for q, skip, limit, expected_nums_and_titles in test_data:
            expected_data = [
                Song(**song_data, title=title, number=num, language=lang)
                for num, title in expected_nums_and_titles
            ]
            expected = ml.Result.OK(
                PaginatedResponse(data=expected_data, skip=skip, limit=limit)
            )
            res = await hymns.query_songs_by_title(
                service, q, language=lang, skip=skip, limit=limit
            )

            res.value.data.sort(key=song_key_func)
            expected.value.data.sort(key=song_key_func)
            assert res == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("service", hymns_service_fixture)
async def test_query_song_by_number(service: HymnsService):
    """query_song_by_title queries for songs whose song number start with a given set of digits"""
    song_data = dict(
        key=MusicalNote.F_MAJOR,
        lines=[[LineSection(note=MusicalNote.F_MAJOR, words="hey you")]],
    )
    nums_and_titles = [
        (1, "foo"),
        (2, "food"),
        (11, "fell"),
        (20, "fish"),
        (2029, "yell"),
        (111, "yearn"),
        (22, "yeast"),
        (110, "yogurt"),
    ]

    test_data = [
        (1, 0, 0, [(1, "foo"), (11, "fell"), (111, "yearn"), (110, "yogurt")]),
        (1, 0, 2, [(1, "foo"), (11, "fell")]),
        (1, 2, 0, [(111, "yearn"), (110, "yogurt")]),
        (11, 0, 0, [(11, "fell"), (111, "yearn"), (110, "yogurt")]),
        (111, 0, 0, [(111, "yearn")]),
        (110, 0, 0, [(110, "yogurt")]),
        (110, 1, 1, []),
        (2, 0, 0, [(2, "food"), (20, "fish"), (2029, "yell"), (22, "yeast")]),
        (20, 0, 0, [(20, "fish"), (2029, "yell")]),
        (20, 1, 1, [(2029, "yell")]),
        (202, 0, 0, [(2029, "yell")]),
        (22, 0, 0, [(22, "yeast")]),
    ]

    for lang in languages:
        for num, title in nums_and_titles:
            song = Song(**song_data, title=title, number=num, language=lang)
            await hymns.add_song(service, song=song)

    for lang in languages:
        for q, skip, limit, expected_nums_and_titles in test_data:
            expected_data = [
                Song(**song_data, title=title, number=num, language=lang)
                for num, title in expected_nums_and_titles
            ]
            expected = ml.Result.OK(
                PaginatedResponse(data=expected_data, skip=skip, limit=limit)
            )
            res = await hymns.query_songs_by_number(
                service, q, language=lang, skip=skip, limit=limit
            )

            res.value.data.sort(key=song_key_func)
            expected.value.data.sort(key=song_key_func)
            assert res == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song", songs_fixture)
async def test_delete_song_requires_title_or_number(service: HymnsService, song: Song):
    """delete_song requires a number or a title or returns a result with a ValidationError"""
    await hymns.add_song(service, song=song)
    res = await hymns.delete_song(service)
    err = _extract_exception(res)
    assert isinstance(err, ValidationError)
    await _assert_song_exists(service, song)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song", songs_fixture)
async def test_delete_song_not_found(service: HymnsService, song: Song):
    """delete_song a non existent song returns a result with a NotFoundError"""
    res = await hymns.delete_song(service, title=song.title)
    err = _extract_exception(res)
    assert isinstance(err, NotFoundError)

    res = await hymns.delete_song(service, number=song.number)
    err = _extract_exception(res)
    assert isinstance(err, NotFoundError)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, langs", songs_langs_fixture)
async def test_delete_song_by_title_all_langs(
    service: HymnsService, song: Song, langs: List[str]
):
    """delete_song removes the song of the given title from all languages from the hymns store"""
    song_versions = [
        Song(
            **{
                **song.dict(),
                "language": lang,
                "title": f"{song.title}title_all_langs",
                "number": song.number + 30,
            }
        )
        for lang in langs
    ]

    for song in song_versions:
        await hymns.add_song(service, song=song)

    res = await hymns.delete_song(service, title=song_versions[0].title)
    assert res == ml.Result.OK(song_versions)

    for song in song_versions:
        await _assert_song_does_not_exist(service, song)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, langs", songs_langs_fixture)
async def test_delete_song_by_number_all_langs(
    service: HymnsService, song: Song, langs: List[str]
):
    """delete_song removes the song of the given number from all languages from the hymns store"""
    song_versions = [
        Song(
            **{
                **song.dict(),
                "language": lang,
                "title": f"{song.title}number_all_langs",
                "number": song.number + 35,
            }
        )
        for lang in langs
    ]

    for song_version in song_versions:
        await hymns.add_song(service, song=song_version)

    number = song_versions[0].number

    res = await hymns.delete_song(service, number=number)
    expected = ml.Result.OK(song_versions)
    res.value.sort(key=song_key_func)
    expected.value.sort(key=song_key_func)
    assert res == expected

    for song_version in song_versions:
        await _assert_song_does_not_exist(service, song_version)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, langs", songs_langs_fixture)
async def test_delete_song_by_title_one_lang(
    service: HymnsService, song: Song, langs: List[str]
):
    """delete_song removes the song of the given title from one language from the hymns store"""
    song_versions = {
        lang: Song(
            **{
                **song.dict(),
                "language": lang,
                "title": f"{song.title}title_one_lang",
                "number": song.number + 25,
            }
        )
        for lang in langs
    }

    for song_version in song_versions.values():
        await hymns.add_song(service, song=song_version)

    for lang in langs:
        song_version = song_versions[lang]
        await _assert_song_exists(service, song_version)

        res = await hymns.delete_song(service, title=song_version.title, language=lang)
        assert res == ml.Result.OK([song_version])

        await _assert_song_does_not_exist(service, song_version)


@pytest.mark.asyncio
@pytest.mark.parametrize("service, song, langs", songs_langs_fixture)
async def test_delete_song_by_number_one_lang(
    service: HymnsService, song: Song, langs: List[str]
):
    """delete_song removes the song of the given number from one language from the hymns store"""
    song_versions = {
        lang: Song(
            **{
                **song.dict(),
                "language": lang,
                "title": f"{song.title}number_one_lang",
                "number": song.number + 15,
            }
        )
        for lang in langs
    }

    for song_version in song_versions.values():
        await hymns.add_song(service, song=song_version)

    for lang in langs:
        song_version = song_versions[lang]
        await _assert_song_exists(service, song_version)

        res = await hymns.delete_song(
            service, number=song_version.number, language=lang
        )
        assert res == ml.Result.OK([song_version])

        await _assert_song_does_not_exist(service, song_version)


async def _assert_song_exists(service, song):
    """Asserts that the song exists in the service"""
    res = await hymns.get_song_by_title(
        service, title=song.title, language=song.language
    )
    assert res == ml.Result.OK(song)


def song_key_func(v: Song) -> str:
    """the sort key function for sorting song lists uniformly"""
    return f"{v.number}{v.language}{v.title}"


async def _assert_song_does_not_exist(service, song):
    """Asserts that the song does not exist in the service"""
    res = await hymns.get_song_by_title(
        service, title=song.title, language=song.language
    )
    err = _extract_exception(res)
    assert isinstance(err, NotFoundError)

    res = await hymns.get_song_by_number(
        service, number=song.number, language=song.language
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
