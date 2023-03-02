from typing import List

import pytest
from fastapi.testclient import TestClient
from api.models import Song
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
