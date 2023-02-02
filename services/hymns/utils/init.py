"""Utility functions for handling initializing the service"""
import funml as ml

from typing import TYPE_CHECKING

from services.config import get_numbers_store, get_titles_store
from services.hymns.data_types import LanguageStore, HymnsService

if TYPE_CHECKING:
    from typing import Callable
    from ...config import ServiceConfig

get_lang_store = lambda v: LanguageStore(
    numbers_store=get_numbers_store(v),
    titles_store=get_titles_store(v),
)  # type: Callable[[str], LanguageStore]
"""Gets the LanguageStore for the given language"""


get_all_lang_stores = lambda conf: (
    ml.val(conf.languages)
    >> ml.imap(lambda lang: (lang, get_lang_store(lang)))
    >> ml.ireduce(lambda acc, curr: {**acc, curr[0]: curr[1]}, initial={})
    >> ml.execute()
)  # type: Callable[[ServiceConfig], dict[str, LanguageStore]]
"""Gets the dictionary of languages and their stores in the config"""


init_hymns_service = lambda stores: HymnsService(
    stores=stores
)  # type: Callable[[dict[str, LanguageStore]], "HymnsService"]
"""Initializes a new hymns service given a dictionary of language stores"""
