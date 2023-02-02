"""Utility functions for handling get operations"""
from typing import TYPE_CHECKING, NamedTuple
import funml as ml

from services.hymns.models import Song
from services.utils import await_output, if_else
import shared as shared_utils

if TYPE_CHECKING:
    from typing import Callable, Optional
    from collections import Awaitable
    from ..data_types import LanguageStore


get_song_by_title = lambda args: (
    ml.val(args.title)
    >> args.store.titles_store.get
    >> await_output
    >> shared_utils.convert_json_to_song
    >> ml.execute()
)  # type: Callable[[GetFromStoreArgs], Awaitable[Song]]
"""Gets a given song by title from the given language store"""


get_song_by_number = lambda args: (
    ml.val(args.number)
    >> args.store.numbers_store.get
    >> await_output
    >> shared_utils.convert_json_to_song
    >> ml.execute()
)  # type: Callable[[GetFromStoreArgs], Awaitable[Song]]
"""Gets a given song by number from the given language store"""


get_song_by_title_or_number = lambda args: (
    if_else(
        check=args.is_title_defined, do=get_song_by_title, else_do=get_song_by_number
    )
    >> await_output
    >> ml.execute()
)
"""Gets a song by either title or number"""


"""
Data Types
"""


class GetFromStoreArgs(NamedTuple):
    """The type of parameter used when getting from store"""

    store: "LanguageStore"
    title: Optional[str] = None
    number: Optional[int] = None

    def is_title_defined(self, *args) -> bool:
        """Checks whether the title is defined"""
        return self.title is not None
