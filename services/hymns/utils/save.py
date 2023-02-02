"""Utility functions and types for handling save to database operations"""
from typing import TYPE_CHECKING, NamedTuple

import funml as ml

from services.config import add_new_language
from services.hymns.models import Song
from services.utils import await_output, new_pipeline_of

if TYPE_CHECKING:
    from typing import Callable
    from collections import Awaitable
    from ..data_types import AddSongArgs, LanguageStore


"""
Main Expressions
"""
save_song = lambda args: (
    ml.val(
        SaveToStoreArgs(store=args.service.stores[args.song.language], song=args.song)
    )
    >> save_to_titles_store
    >> await_output
    >> new_pipeline_of(
        SaveToStoreArgs(store=args.service.stores[args.song.language], song=args.song)
    )
    >> save_to_numbers_store
    >> await_output
    >> ml.execute()
)  # type: Callable[[AddSongArgs], Awaitable[None]]
"""Saves the given song in the language store, both in the numbers and in the titles store"""

save_lang_and_song = lambda args: (
    new_pipeline_of(args.song.language)
    >> add_new_language
    >> await_output
    >> new_pipeline_of(args)
    >> save_song
    >> await_output
    >> ml.execute()
)  # type: Callable[[AddSongArgs], Awaitable[None]]
"""Save both language and song"""


"""
Primitive Expressions
"""
save_to_titles_store = lambda args: args.store.titles_store.set(
    args.song.title, args.song.json()
)  # type: Callable[[SaveToStoreArgs], Awaitable[None]]
"""Saves song in the async store that has song titles as keys"""


save_to_numbers_store = lambda args: args.store.numbers_store.set(
    args.song.number, args.song.json()
)  # type: Callable[[SaveToStoreArgs], Awaitable[None]]
"""Saves song in the async store that has song number as keys"""


"""
Data Types
"""


class SaveToStoreArgs(NamedTuple):
    """The type of parameter used when saving to store"""

    store: "LanguageStore"
    song: Song
