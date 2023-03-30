"""Utilities common to all services"""

from pydantic import BaseModel


class Config(BaseModel):
    """Base class for all configs"""
