from collections import Awaitable
from typing import Callable, TYPE_CHECKING
import funml as ml

from services.config import (
    ServiceConfig,
)
from services.hymns.utils.delete import delete_from_one_store, delete_from_all_stores
from services.hymns.utils.get import (
    GetFromStoreArgs,
    get_song_by_number as get_raw_song_by_number,
    get_song_by_title as get_raw_song_by_title,
)
from services.hymns.utils.init import get_all_lang_stores, init_hymns_service
from services.hymns.utils.save import save_song, save_lang_and_song
from services.hymns.utils.search import query_store_by_title, SearchArgs
from services.hymns.utils.shared import err_if_none

from services.utils import if_else, to_result

if TYPE_CHECKING:
    from data_types import (
        AddSongArgs,
        DeleteSongArgs,
        GetSongByTitleArgs,
        GetSongByNumberArgs,
        QuerySongByTitleArgs,
    )


"""Main Expressions"""
initialize = (
    lambda conf: ml.val(conf)
    >> get_all_lang_stores
    >> init_hymns_service
    >> ml.execute()
)  # type: Callable[[ServiceConfig], "HymnsService"]
"""Initializes the hymns service given the configuration"""


add_song = lambda args: (
    ml.val(args)
    >> if_else(
        check=args.is_lang_available,
        do=save_song,
        else_do=save_lang_and_song,
    )
    >> to_result
    >> ml.execute()
)  # type: Callable[[AddSongArgs], Awaitable[ml.Result]]
"""Adds a song to the hymns service"""


delete_song = lambda args: (
    if_else(
        check=args.is_lang_defined,
        do=delete_from_one_store,
        else_do=delete_from_all_stores,
    )
    >> to_result
    >> ml.execute()
)  # type: Callable[[DeleteSongArgs], Awaitable[ml.Result]]
"""Deletes the song of the given number or title or both"""


get_song_by_title = lambda args: (
    ml.val(GetFromStoreArgs(store=args.service.stores[args.language], title=args.title))
    >> get_raw_song_by_title
    >> err_if_none(item=args.title)
    >> to_result
    >> ml.execute()
)  # type: Callable[[GetSongByTitleArgs], Awaitable[ml.Result]]
"""Gets a song by title and language"""


get_song_by_number = lambda args: (
    ml.val(
        GetFromStoreArgs(store=args.service.stores[args.language], number=args.number)
    )
    >> get_raw_song_by_number
    >> err_if_none(item=args.number)
    >> to_result
    >> ml.execute()
)  # type: Callable[[GetSongByNumberArgs], Awaitable[ml.Result]]
"""Gets a song by number and language"""


query_song_by_title = lambda args: (
    ml.val(
        SearchArgs(
            store=args.service.stores[args.language],
            q=args.q,
            skip=args.skip,
            limit=args.limit,
        )
    )
    >> query_store_by_title
    >> to_result
    >> ml.execute()
)  # type: Callable[[QuerySongByTitleArgs], Awaitable[ml.Result]]
"""Gets a song by title and language"""
