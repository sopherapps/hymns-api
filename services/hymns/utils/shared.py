"""Utilities common to many operations"""
import json
from typing import TYPE_CHECKING

import funml as ml

from services.hymns.errors import NotFoundError
from services.hymns.models import Song
from services.utils import if_else

if TYPE_CHECKING:
    from typing import Callable

convert_json_to_song = lambda v: Song(**json.loads(v))  # type: Callable[[dict], Song]
"""Converts a dict into a Song"""

err_if_none = lambda item: if_else(
    check=(lambda arg: arg is None),
    do=lambda arg: ml.Result.ERR(NotFoundError(item)),
    else_do=lambda arg: ml.Result.OK(arg),
)
"""Creates an expression that returns an error if argument is None or else returns the value an ml.Result.OK """
