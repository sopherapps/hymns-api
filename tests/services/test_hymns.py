import pytest


@pytest.mark.asyncio
async def test_initialize():
    """initialize initializes the hymns store and everything required"""
    pass


@pytest.mark.asyncio
async def test_add_song():
    """add_song adds a given song to the hymns store"""
    pass


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
