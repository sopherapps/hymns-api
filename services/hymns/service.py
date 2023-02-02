from collections import Awaitable
from typing import Callable, TYPE_CHECKING
import funml as ml

from services.config import (
    ServiceConfig,
)

import services.hymns.utils.init as init_utils
import services.hymns.utils.save as save_utils
import services.hymns.utils.delete as del_utils
import services.hymns.utils.get as get_utils
import services.hymns.utils.search as search_utils
import services.hymns.utils.shared as shared_utils
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
    >> init_utils.get_all_lang_stores
    >> init_utils.init_hymns_service
    >> ml.execute()
)  # type: Callable[[ServiceConfig], "HymnsService"]
"""Initializes the hymns service given the configuration"""


add_song = lambda args: (
    ml.val(args)
    >> if_else(
        check=args.is_lang_available,
        do=save_utils.save_song,
        else_do=save_utils.save_lang_and_song,
    )
    >> to_result
    >> ml.execute()
)  # type: Callable[[AddSongArgs], Awaitable[ml.Result]]
"""Adds a song to the hymns service"""


delete_song = lambda args: (
    if_else(
        check=args.is_lang_defined,
        do=del_utils.delete_from_one_store,
        else_do=del_utils.delete_from_all_stores,
    )
    >> to_result
    >> ml.execute()
)  # type: Callable[[DeleteSongArgs], Awaitable[ml.Result]]
"""Deletes the song of the given number or title or both"""


get_song_by_title = lambda args: (
    ml.val(
        get_utils.GetFromStoreArgs(
            store=args.service.stores[args.language], title=args.title
        )
    )
    >> get_utils.get_song_by_title
    >> shared_utils.err_if_none(item=args.title)
    >> to_result
    >> ml.execute()
)  # type: Callable[[GetSongByTitleArgs], Awaitable[ml.Result]]
"""Gets a song by title and language"""


get_song_by_number = lambda args: (
    ml.val(
        get_utils.GetFromStoreArgs(
            store=args.service.stores[args.language], number=args.number
        )
    )
    >> get_utils.get_song_by_number
    >> shared_utils.err_if_none(item=args.number)
    >> to_result
    >> ml.execute()
)  # type: Callable[[GetSongByNumberArgs], Awaitable[ml.Result]]
"""Gets a song by number and language"""


query_song_by_title = lambda args: (
    ml.val(
        search_utils.SearchArgs(
            store=args.service.stores[args.language],
            q=args.q,
            skip=args.skip,
            limit=args.limit,
        )
    )
    >> search_utils.query_store_by_title
    >> to_result
    >> ml.execute()
)  # type: Callable[[QuerySongByTitleArgs], Awaitable[ml.Result]]
"""Gets a song by title and language"""
