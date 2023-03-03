from typing import List, Dict, Any

import pytest
from fastapi.testclient import TestClient
from api.models import Song, MusicalNote, LineSection, PaginatedResponse
from tests.conftest import api_songs_langs_fixture, languages, api_songs


@pytest.mark.parametrize("client, song, langs", api_songs_langs_fixture)
def test_create_song(client: TestClient, song: Song, langs: List[str]):
    """create_song creates a song"""

    with client:
        for lang in langs:
            new_song = Song(**{**song.dict(), "language": lang})
            payload = new_song.dict()

            response = client.post("/", json=payload)
            assert response.status_code == 200
            assert response.json() == payload

            _assert_song_has_content(
                client, language=lang, number=song.number, content=payload
            )


def test_get_song_detail(test_client: TestClient):
    """get_song_detail gets a song's details"""
    with test_client:
        for lang in languages:
            for song in api_songs:
                new_song = Song(**{**song.dict(), "language": lang})
                payload = new_song.dict()
                response = test_client.post("/", json=payload)
                assert response.status_code == 200

        for song in api_songs:
            expected = dict(
                number=song.number,
                translations={
                    lang: {**song.dict(), "language": lang} for lang in languages
                },
            )
            response = test_client.get(
                f"/{languages[0]}/{song.number}", params={"translation": languages[1:]}
            )
            assert response.status_code == 200
            assert response.json() == expected


@pytest.mark.parametrize("client, song, langs", api_songs_langs_fixture)
def test_update_song(client: TestClient, song: Song, langs: List[str]):
    """Updates the keys and or the lines of the song"""
    test_data = [
        dict(key="G#m", lines=[[dict(note="Am", words=f"{song.title} changed")]]),
        dict(
            lines=[
                [
                    dict(note="Am", words="woo hoo"),
                    dict(note="Gm", words="yeah hoo"),
                ],
                [
                    dict(note="Cm", words="see-yah"),
                    dict(note="Dm", words="woolululu"),
                ],
            ]
        ),
        dict(key="D"),
    ]

    with client:
        for new_data in test_data:
            for lang in langs:
                new_song = Song(**{**song.dict(), "language": lang})
                payload = new_song.dict()
                expected = {**payload, **new_data}

                response = client.post("/", json=payload)
                assert response.status_code == 200

                response = client.put(f"/{lang}/{song.number}", json=new_data)
                assert response.status_code == 200
                assert response.json() == expected

                _assert_song_has_content(
                    client, language=lang, number=song.number, content=expected
                )


def test_delete_song(test_client: TestClient):
    """Deletes the song of the given song number"""
    with test_client:
        for lang in languages:
            for song in api_songs:
                new_song = Song(**{**song.dict(), "language": lang})
                payload = new_song.dict()
                response = test_client.post("/", json=payload)
                assert response.status_code == 200

        for lang in languages:
            for song in api_songs:
                expected = Song(**{**song.dict(), "language": lang}).dict()
                response = test_client.delete(f"/{lang}/{song.number}")
                assert response.status_code == 200
                assert response.json() == expected

                response = test_client.get(f"/{lang}/{song.number}")
                assert response.status_code == 404


def test_query_by_title(test_client: TestClient):
    """Queries by title of the song"""
    song_data = dict(
        key="F",
        lines=[[dict(note="F", words="hey you")]],
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

    with test_client:
        for lang in languages:
            for num, title in nums_and_titles:
                payload = dict(**song_data, title=title, number=num, language=lang)
                response = test_client.post("/", json=payload)
                assert response.status_code == 200

        for lang in languages:
            for q, skip, limit, expected_nums_and_titles in test_data:
                expected = [
                    dict(**song_data, title=title, number=num, language=lang)
                    for num, title in expected_nums_and_titles
                ]
                response = test_client.get(
                    f"/{lang}/find-by-title/{q}", params=dict(skip=skip, limit=limit)
                )
                assert response.status_code == 200
                assert response.json() == dict(data=expected, skip=skip, limit=limit)


def test_query_by_number(test_client: TestClient):
    """Queries by number of the song"""
    song_data = dict(
        key="F",
        lines=[[dict(note="F", words="hey you")]],
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

    with test_client:
        for lang in languages:
            for num, title in nums_and_titles:
                payload = dict(**song_data, title=title, number=num, language=lang)
                response = test_client.post("/", json=payload)
                assert response.status_code == 200

        for lang in languages:
            for q, skip, limit, expected_nums_and_titles in test_data:
                expected = [
                    dict(**song_data, title=title, number=num, language=lang)
                    for num, title in expected_nums_and_titles
                ]
                response = test_client.get(
                    f"/{lang}/find-by-number/{q}", params=dict(skip=skip, limit=limit)
                )
                assert response.status_code == 200
                assert response.json() == dict(data=expected, skip=skip, limit=limit)


def _assert_song_has_content(
    client: TestClient, language: str, number: int, content: Dict[str, Any]
):
    """Asserts that the song for the given language and number has the given content"""
    response = client.get(f"/{language}/{number}")
    assert response.status_code == 200
    assert response.json() == dict(number=number, translations={language: content})
