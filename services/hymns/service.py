import json
from collections import Awaitable
from typing import Callable, Optional
import funml as ml

from py_scdb import AsyncStore

from services.config import (
    ServiceConfig,
    get_titles_store,
    get_numbers_store,
    add_new_language,
)
from services.hymns.models import Song
from services.utils import if_else, to_result, await_output, from_data

"""
Data Types
"""


@ml.record
class LanguageStore:
    """The collective store for the given language having all stores for that language.

    It includes two stores; one where the song titles are the keys and the other where
    the song numbers are the keys.

    Attributes:
        titles_store: the AsyncStore whose keys are the song titles
        numbers_store: the AsyncStore whose keys are the song numbers
    """

    titles_store: AsyncStore
    numbers_store: AsyncStore


@ml.record
class HymnsService:
    stores: dict[str, LanguageStore] = {}


"""
Primitive Expressions
"""
_get_lang_store = lambda v: LanguageStore(
    numbers_store=get_numbers_store(v),
    titles_store=get_titles_store(v),
)  # type: Callable[[str], LanguageStore]
"""Gets the LanguageStore for the given language"""


_get_all_lang_stores = lambda conf: (
    ml.val(conf.languages)
    >> ml.imap(lambda lang: (lang, _get_lang_store(lang)))
    >> ml.ireduce(lambda acc, curr: {**acc, curr[0]: curr[1]}, initial={})
    >> ml.execute()
)  # type: Callable[[ServiceConfig], dict[str, LanguageStore]]
"""Gets the dictionary of languages and their stores in the config"""


__save_to_titles_store_util = lambda store, song: store.set(
    song.title, song.json()
)  # type: Callable[[AsyncStore, Song], Awaitable[None]]
"""Saves song in the async store that has song titles as keys"""

_save_to_titles_store = lambda store_song_pair: __save_to_titles_store_util(
    *store_song_pair
)  # type: Callable[[tuple[AsyncStore, Song]], Awaitable[None]]
"""Saves song in the async store that has song titles as keys"""


__save_to_numbers_store_util = lambda store, song: store.set(
    song.number, song.json()
)  # type: Callable[[AsyncStore, Song], Awaitable[None]]
"""Saves song in the async store that has song number as keys"""


_save_to_numbers_store = lambda store_song_pair: __save_to_numbers_store_util(
    *store_song_pair
)  # type: Callable[[tuple[AsyncStore, Song]], Awaitable[None]]
"""Saves song in the async store that has song number as keys"""


_delete_from_titles_store = lambda title, store: store.delete(
    title
)  # type: Callable[[str, AsyncStore], Awaitable[ml.Result]]
"""Removes song of the given song title from the async store that has song titles as keys"""


_delete_from_numbers_store = lambda number, store: store.delete(
    number
)  # type: Callable[[int, AsyncStore], Awaitable[ml.Result]]
"""Removes song of the given song number from the async store that has song numbers as keys"""


_song_from_dict = lambda v: Song(**v)  # type: Callable[[dict], Song]
"""Converts a dict into a Song"""


_song_from_json = lambda v: Song(**json.loads(v))  # type: Callable[[dict], Song]
"""Converts a dict into a Song"""


__get_song_by_title_util = lambda store, title: (
    ml.val(title)
    >> store.by_titles_store.get
    >> await_output
    >> _song_from_json
    >> ml.execute()
)  # type: Callable[[LanguageStore, str], Awaitable[Song]]
"""Gets a given song by title from the given language store"""

_get_song_by_title = lambda store_title_pair: __get_song_by_title_util(
    *store_title_pair
)  # type: Callable[[tuple[LanguageStore, str]], Awaitable[Song]]
"""Gets a given song by title from the given language store"""


__get_song_by_number_util = lambda store, number: (
    ml.val(number)
    >> store.numbers_store.get
    >> await_output
    >> _song_from_json
    >> ml.execute()
)  # type: Callable[[LanguageStore, int], Awaitable[Song]]
"""Gets a given song by number from the given language store"""

_get_song_by_number = lambda store_number_pair: __get_song_by_number_util(
    *store_number_pair
)  # type: Callable[[tuple[LanguageStore, int]], Awaitable[Song]]
"""Gets a given song by number from the given language store"""


__query_store_by_title_util = lambda store, q, skip=0, limit=0: (
    ml.val((q, skip, limit))
    >> store.titles_store.search
    >> await_output
    >> ml.imap(_song_from_json)
)  # type: Callable[[LanguageStore, str, int, int], Awaitable[list[Song]]]
"""Gets a list of songs whose titles begin with the search term"""


_query_store_by_title = lambda args: __query_store_by_title_util(
    *args
)  # type: Callable[[tuple[LanguageStore, str, int, int]], Awaitable[list[Song]]]
"""Gets a list of songs whose titles begin with the search term"""

_save_song = lambda service, song: (
    ml.val((service.stores[song.language], song))
    >> _save_to_titles_store
    >> await_output
    >> from_data(
        (
            service.stores[song.language],
            song,
        )
    )
    >> _save_to_numbers_store
    >> await_output
    >> ml.execute()
)  # type: Callable[["HymnsService", Song], Awaitable[None]]
"""Saves the given song in the language store, both in the numbers and in the titles store"""

_save_lang_and_song = lambda service, song: (
    from_data(song.language)
    >> add_new_language
    >> await_output
    >> from_data((service, song))
    >> _save_song
    >> await_output
    >> ml.execute()
)  # type: Callable[["HymnsService", Song], Awaitable[None]]
"""Save language while allowing service and song params to pass through this step"""


async def _delete_from_store(
    store: LanguageStore, title: str = None, number: int = None
):
    """Removes the song of given title or number from the language store"""
    is_title_set = title is not None
    is_number_set = number is not None

    if not is_title_set and not is_number_set:
        raise ValueError("no title or number was supplied for deletion")

    song: Optional[Song] = None
    if is_title_set:
        song = await __get_song_by_title_util(store, title)
    elif song is None and is_number_set:
        song = await __get_song_by_number_util(store, number)

    await _delete_from_titles_store(title=song.title, store=store)
    await _delete_from_numbers_store(number=song.number, store=store)


_delete_from_all_stores = (
    lambda service, title=None, number=None: ml.val(service.stores.values)
    >> ml.imap(
        lambda store: await_output(
            _delete_from_store(store, title=title, number=number)
        )
    )
    >> ml.execute()
)  # type: Callable[["HymnsService", str, int], Awaitable[None]]
"""Removes the given song from all lang stores"""

_is_lang_available = (
    lambda service, song: song.language in service.stores
)  # type: Callable[["HymnsService", Song], bool]
"""Checks whether a given language is available in the HymnsService"""

init_hymns_service = lambda stores: HymnsService(
    stores=stores
)  # type: Callable[[dict[str, LanguageStore]], "HymnsService"]
"""Initializes a new hymns service given a dictionary of language stores"""


"""Main Expressions"""
initialize = (
    lambda conf: ml.val(_get_all_lang_stores) >> init_hymns_service >> ml.execute()
)  # type: Callable[[ServiceConfig], "HymnsService"]
"""Initializes the hymns service given the configuration"""


add_song = lambda service, song: (
    ml.val((service, song))
    >> if_else(
        check=_is_lang_available,
        do=_save_song,
        else_do=(ml.val(_save_lang_and_song) >> _save_song >> ml.execute()),
    )
    >> to_result
    >> ml.execute()
)  # type: Callable[["HymnsService", Song], Awaitable[ml.Result]]
"""Adds a song to the hymns service"""


delete_song = lambda service, lang=None, title=None, number=None: (
    if_else(
        check=(lambda: lang is None),
        do=lambda: _delete_from_all_stores(service, title, number),
        else_do=lambda: _delete_from_store(service.stores[lang], title, number),
    )
    >> to_result
    >> ml.execute()
)  # type: Callable[["HymnsService", str, str, int], Awaitable[ml.Result]]
"""Deletes the song of the given number or title or both"""


get_song_by_title = lambda service, lang, title: (
    ml.val((service.stores[lang], title))
    >> _get_song_by_title
    >> to_result
    >> ml.execute()
)  # type: Callable[["HymnsService", str, str], Awaitable[ml.Result]]
"""Gets a song by title and language"""


get_song_by_number = lambda service, lang, number: (
    ml.val((service.stores[lang], number))
    >> _get_song_by_number
    >> to_result
    >> ml.execute()
)  # type: Callable[["HymnsService", str, str], Awaitable[ml.Result]]
"""Gets a song by number and language"""


query_song_by_title = lambda service, lang, q, skip=0, limit=0: (
    ml.val((service, lang, q, skip, limit))
    >> _query_store_by_title
    >> to_result
    >> ml.execute()
)  # type: Callable[["HymnsService", str, str, int, int], Awaitable[ml.Result]]
"""Gets a song by title and language"""
