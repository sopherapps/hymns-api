import time
from typing import List, Dict, Any

import funml as ml
import pytest
from fastapi.testclient import TestClient
from api.models import Song
from services import auth
from .conftest import api_songs_langs_fixture, get_rate_limit_string, languages, songs
from ...utils.shared import otp_email_regex


@pytest.mark.asyncio
@pytest.mark.parametrize("client, song, langs", api_songs_langs_fixture)
async def test_create_song(client: TestClient, song: Song, langs: List[str]):
    """create_song creates a song"""

    with client:
        headers = await _get_auth_headers(client)

        for lang in langs:
            new_song = Song(**{**song.dict(), "language": lang})
            payload = new_song.dict()

            response = client.post("/", json=payload, headers=headers)
            assert response.status_code == 200
            assert response.json() == payload

            _assert_song_has_content(
                client,
                language=lang,
                number=song.number,
                content=payload,
                headers=headers,
            )


@pytest.mark.asyncio
async def test_get_song_detail(test_client: TestClient):
    """get_song_detail gets a song's details"""
    with test_client:
        headers = await _get_auth_headers(test_client)

        for lang in languages:
            for song in songs:
                new_song = Song(**{**song.dict(), "language": lang})
                payload = new_song.dict()
                response = test_client.post("/", json=payload, headers=headers)
                assert response.status_code == 200

        for song in songs:
            expected = dict(
                number=song.number,
                translations={
                    lang: {**song.dict(), "language": lang} for lang in languages
                },
            )
            response = test_client.get(
                f"/{languages[0]}/{song.number}",
                params={"translation": languages[1:]},
                headers=headers,
            )
            assert response.status_code == 200
            assert response.json() == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("client, song, langs", api_songs_langs_fixture)
async def test_update_song(client: TestClient, song: Song, langs: List[str]):
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
        headers = await _get_auth_headers(client)

        for new_data in test_data:
            for lang in langs:
                new_song = Song(**{**song.dict(), "language": lang})
                payload = new_song.dict()
                expected = {**payload, **new_data}

                response = client.post("/", json=payload, headers=headers)
                assert response.status_code == 200

                response = client.put(
                    f"/{lang}/{song.number}", json=new_data, headers=headers
                )
                assert response.status_code == 200
                assert response.json() == expected

                _assert_song_has_content(
                    client,
                    language=lang,
                    number=song.number,
                    content=expected,
                    headers=headers,
                )


@pytest.mark.asyncio
async def test_delete_song(test_client: TestClient):
    """Deletes the song of the given song number"""
    with test_client:
        headers = await _get_auth_headers(test_client)

        for lang in languages:
            for song in songs:
                new_song = Song(**{**song.dict(), "language": lang})
                payload = new_song.dict()
                response = test_client.post("/", json=payload, headers=headers)
                assert response.status_code == 200

        for lang in languages:
            for song in songs:
                expected = [Song(**{**song.dict(), "language": lang}).dict()]
                response = test_client.delete(f"/{lang}/{song.number}", headers=headers)
                assert response.status_code == 200
                assert response.json() == expected

                response = test_client.get(f"/{lang}/{song.number}", headers=headers)
                assert response.status_code == 404


@pytest.mark.asyncio
async def test_query_by_title(test_client: TestClient):
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
        headers = await _get_auth_headers(test_client)

        for lang in languages:
            for num, title in nums_and_titles:
                payload = dict(**song_data, title=title, number=num, language=lang)
                response = test_client.post("/", json=payload, headers=headers)
                assert response.status_code == 200

        for lang in languages:
            for q, skip, limit, expected_nums_and_titles in test_data:
                expected = [
                    dict(**song_data, title=title, number=num, language=lang)
                    for num, title in expected_nums_and_titles
                ]
                response = test_client.get(
                    f"/{lang}/find-by-title/{q}",
                    params=dict(skip=skip, limit=limit),
                    headers=headers,
                )
                assert response.status_code == 200
                assert response.json() == dict(data=expected, skip=skip, limit=limit)


@pytest.mark.asyncio
async def test_query_by_number(test_client: TestClient):
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
        headers = await _get_auth_headers(test_client)

        for lang in languages:
            for num, title in nums_and_titles:
                payload = dict(**song_data, title=title, number=num, language=lang)
                response = test_client.post("/", json=payload, headers=headers)
                assert response.status_code == 200

        for lang in languages:
            for q, skip, limit, expected_nums_and_titles in test_data:
                expected = [
                    dict(**song_data, title=title, number=num, language=lang)
                    for num, title in expected_nums_and_titles
                ]
                response = test_client.get(
                    f"/{lang}/find-by-number/{q}",
                    params=dict(skip=skip, limit=limit),
                    headers=headers,
                )
                assert response.status_code == 200
                assert response.json() == dict(data=expected, skip=skip, limit=limit)


@pytest.mark.asyncio
async def test_api_key(test_client: TestClient):
    """Some routes expect an API key in the headers"""
    routes = [
        ("GET", "/english/find-by-number/1", {}, dict(skip=0, limit=0)),
        ("GET", "/english/find-by-title/Bar", {}, dict(skip=0, limit=0)),
        ("GET", "/english/1", {}, {}),
    ]
    with test_client:
        api_key = _get_api_key(test_client)
        jwt_token = await _get_oauth2_token(test_client)
        default_headers = {"Authorization": f"Bearer {jwt_token}"}

        headers = {**default_headers, "x-api-key": api_key}
        no_api_key_headers = {**default_headers, "Content-Type": "application/json"}
        wrong_api_key_headers = {**default_headers, "x-api-key": f"{api_key[:-3]}you"}

        for song in songs:
            payload = song.dict()
            response = test_client.post("/", json=payload, headers=headers)
            assert response.status_code == 200

        for method, route, body, params in routes:
            response = test_client.request(
                method, url=route, json=body, params=params, headers=no_api_key_headers
            )
            assert response.status_code == 403
            assert response.json() == {"detail": "Not authenticated"}

            response = test_client.request(
                method,
                url=route,
                json=body,
                params=params,
                headers=wrong_api_key_headers,
            )
            assert response.status_code == 403
            assert response.json() == {"detail": "could not validate credentials"}

            response = test_client.request(
                method, url=route, json=body, params=params, headers=headers
            )
            assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_oauth2_token(test_client: TestClient):
    """Some routes expect an oauth2 JWT token in the headers"""
    routes = [
        ("POST", "/", songs[0].dict(), {}),
        ("PUT", "/english/1", songs[0].dict(), {}),
        ("DELETE", "/english/1", songs[0].dict(), {}),
    ]
    with test_client:
        jwt_token = await _get_oauth2_token(test_client)
        headers = {"Authorization": f"Bearer {jwt_token}"}
        no_jwt_token_headers = {"Content-Type": "application/json"}
        wrong_jwt_token_headers = {"Authorization": f"Bearer {jwt_token[:-3]}you"}

        for song in songs:
            payload = song.dict()
            response = test_client.post("/", json=payload, headers=headers)
            assert response.status_code == 200

        for method, route, body, params in routes:
            response = test_client.request(
                method,
                url=route,
                json=body,
                params=params,
                headers=no_jwt_token_headers,
            )
            assert response.status_code == 401
            assert response.json() == {"detail": "Not authenticated"}

            response = test_client.request(
                method,
                url=route,
                json=body,
                params=params,
                headers=wrong_jwt_token_headers,
            )
            assert response.status_code == 403
            assert response.json() == {"detail": "AuthenticationError: invalid token"}

            response = test_client.request(
                method, url=route, json=body, params=params, headers=headers
            )
            assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_rate_limit(test_client_and_rate_limit):
    """All routes are protected by a rate limiter, whose rate is set using an environment variable"""
    client, max_reqs_per_sec = test_client_and_rate_limit
    routes = [
        ("GET", "/english/find-by-number/1", {}, dict(skip=0, limit=0)),
        ("GET", "/english/find-by-title/Bar", {}, dict(skip=0, limit=0)),
        ("GET", "/english/1", {}, {}),
        ("POST", "/", songs[0].dict(), {}),
        ("PUT", "/english/1", songs[0].dict(), {}),
        ("DELETE", "/english/1", songs[0].dict(), {}),
    ]

    with client:
        time.sleep(1)
        headers = await _get_auth_headers(client)

        for song in songs:
            payload = song.dict()
            time.sleep(1)
            response = client.post("/", json=payload, headers=headers)
            assert response.status_code == 200

        for method, route, body, params in routes:
            client.app.state.limiter.reset()

            for _ in range(max_reqs_per_sec):
                response = client.request(
                    method, url=route, json=body, params=params, headers=headers
                )
                assert response.status_code in (200, 404)

            # the next request should throw an error because number of requests per second are exhausted.
            response = client.request(
                method, url=route, json=body, params=params, headers=headers
            )
            assert response.status_code == 429
            assert response.json() == {
                "error": f"Rate limit exceeded: {get_rate_limit_string(max_reqs_per_sec)}"
            }

            time.sleep(1)
            response = client.request(
                method, url=route, json=body, params=params, headers=headers
            )
            assert response.status_code in (200, 404)


def _assert_song_has_content(
    client: TestClient,
    language: str,
    number: int,
    content: Dict[str, Any],
    headers: Dict[str, Any] = {},
):
    """Asserts that the song for the given language and number has the given content"""
    response = client.get(f"/{language}/{number}", headers=headers)
    assert response.status_code == 200
    assert response.json() == dict(number=number, translations={language: content})


async def _get_auth_headers(client):
    """Gets the auth headers to use for the client"""
    return {
        "x-api-key": _get_api_key(client),
        "Authorization": f"Bearer {await _get_oauth2_token(client)}",
    }


def _get_api_key(client: TestClient) -> str:
    """Gets the API key to use to access the API."""
    response = client.post(f"/register", json={})
    assert response.status_code == 200

    data = response.json()
    return data["key"]


async def _get_oauth2_token(client: TestClient) -> str:
    """Gets the Oauth2 token to use to access the admin part of the API."""
    # create new admin user
    user = auth.models.UserDTO(
        username="johndoe",
        email="johndoe@example.com",
        password="johnpassword",
    )
    resp = await auth.create_user(client.app.state.auth_service, user)
    assert isinstance(resp, ml.Result.OK)

    with client.app.state.auth_service.mail.record_messages() as outbox:
        # login with user
        login_request = {"username": user.username, "password": user.password}
        response = client.post("/login", data=login_request)
        assert response.status_code == 200
        unverified_token = response.json()["access_token"]

        # read email to get otp
        assert len(outbox) >= 1
        mail = outbox[-1]
        message_parts = mail.get_payload()
        message = message_parts[0].get_payload(decode=True)
        charset = mail.get_content_charset("iso-8859-1")
        decoded_msg = message.decode(charset, "replace")
        otp = otp_email_regex.search(decoded_msg).group(1)

    # verify OTP
    otp_request = {"otp": otp}
    headers = {"Authorization": f"Bearer {unverified_token}"}
    response = client.post("/verify-otp", json=otp_request, headers=headers)
    assert response.status_code == 200

    # return JWT token
    return response.json()["access_token"]
