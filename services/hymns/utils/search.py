"""Utility functions for handling search operations"""
from typing import NamedTuple, TYPE_CHECKING

import funml as ml

from services.utils import await_output
import shared as shared_utils


if TYPE_CHECKING:
    from typing import Callable
    from collections import Awaitable
    from ..models import Song
    from ..data_types import LanguageStore

"""
Main Expressions
"""
query_store_by_title = lambda args: (
    ml.val(args)
    >> __search_by_title
    >> await_output
    >> ml.imap(shared_utils.convert_json_to_song)
    >> ml.execute()
)  # type: Callable[[SearchArgs], Awaitable[list[Song]]]
"""Gets a list of songs whose titles begin with the search term"""


"""
Primitive Expressions
"""
__search_by_title = lambda args: args.store.titles_store.search(
    term=args.q, skip=args.skip, limit=args.limit
)  # type: Callable[[SearchArgs], Awaitable[list[str]]]
"""Searches the store by title for the given `q`"""


"""
Data Types
"""


class SearchArgs(NamedTuple):
    """The type of parameter used when searching for a given term."""

    store: "LanguageStore"
    q: str
    skip: int
    limit: int
