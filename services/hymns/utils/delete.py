"""Utility functions for handling delete operations"""
from typing import TYPE_CHECKING, NamedTuple

from services.hymns.errors import ValidationError, NotFoundError
import funml as ml

from .get import get_song_by_title_or_number, GetFromStoreArgs

if TYPE_CHECKING:
    from typing import Callable, Optional
    from collections import Awaitable
    from ..data_types import LanguageStore, DeleteSongArgs


delete_from_all_stores = lambda args: (
    ml.val(args.service.stores.values)
    >> ml.imap(
        lambda store: (
            ml.val(
                DeleteFromStoreArgs(store=store, title=args.title, number=args.number)
            )
            >> delete_from_one_store
            >> ml.execute()
        )
    )
    >> ml.execute()
)  # type: Callable[[DeleteSongArgs], Awaitable[None]]
"""Removes the given song from all lang stores"""

delete_from_titles_store = lambda args: args.store.titles_store.delete(
    args.title
)  # type: Callable[[DeleteFromStoreArgs], Awaitable[None]]
"""Removes song of the given song title from the async store that has song titles as keys"""


delete_from_numbers_store = lambda args: args.store.numbers_store.delete(
    args.number
)  # type: Callable[[DeleteFromStoreArgs], Awaitable[None]]
"""Removes song of the given song number from the async store that has song numbers as keys"""


async def delete_from_one_store(args: "DeleteSongArgs"):
    """Removes the song of given title or number from the language store"""
    args = DeleteFromStoreArgs(
        store=args.service.stores[args.language], title=args.title, number=args.number
    )

    args.validate()
    song = await get_song_by_title_or_number(
        GetFromStoreArgs(store=args.store, title=args.title, number=args.number)
    )
    if song is None:
        raise NotFoundError(f"song title: {args.title} or number: {args.number}")
    args_for_delete = DeleteFromStoreArgs(
        store=args.store, title=song.title, number=song.number
    )
    await delete_from_titles_store(args_for_delete)
    await delete_from_numbers_store(args_for_delete)


"""Data Types"""


class DeleteFromStoreArgs(NamedTuple):
    """The type of parameter used when deleting from store"""

    store: "LanguageStore"
    title: Optional[str] = None
    number: Optional[int] = None

    def validate(self):
        """Raises Validation Error if neither title nor number is set"""
        if self.title is None and self.number is None:
            raise ValidationError("no title or number was supplied for deletion")
