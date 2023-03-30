"""module containing the abstract classes for stores and their configuration"""
from abc import abstractmethod
from typing import Optional, List, Tuple, Dict, Type, TypeVar

from pydantic import BaseModel

from errors import ConfigurationError
from services.store.utils import get_store_type
from services.utils import Config

T = TypeVar("T", bound=BaseModel)


class Store:
    """An abstract class to handle storage of data

    ensure to change the __store_type__ and __store_config_cls__ when subclassing

    """

    _registry: Dict[str, Type["Store"]] = {}
    __store_type__: str = "None"
    __store_config_cls__: Type[Config] = Config

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Store._registry[cls.__store_type__] = cls

    def __init__(self, uri: str, name: str, options: Config):
        pass

    @classmethod
    def retrieve_store(cls, uri: str, name: str, options: Config) -> "Store":
        """Retrieves the given store of the given options and store type"""
        store_type = get_store_type(uri)

        try:
            store_cls = Store._registry[store_type]
            store_conf = store_cls.__store_config_cls__(**options.dict())
            return store_cls(uri=uri, name=name, options=store_conf)
        except KeyError:
            raise ConfigurationError(f"store of type: {store_type} does not exist")

    @abstractmethod
    async def set(self, k: str, v: BaseModel, **kwargs) -> None:
        """
        Inserts or updates the key-value pair
        :param k: the key as a UTF-8 string
        :param v: the value as an ml.Record
        :param kwargs: other key-word arguments
        """
        raise NotImplementedError("set not implemented")

    @abstractmethod
    async def get(self, model: Type[T], k: str) -> Optional[T]:
        """
        Gets the value associated with the given key
        :param model: the base model to return
        :param k: the key as a UTF-8 string
        :return: the value if it exists or None if it doesn't
        """
        raise NotImplementedError("get not implemented")

    @abstractmethod
    async def search(
        self, model: Type[T], term: str, skip: int = 0, limit: int = 0
    ) -> List[T]:
        """
        Finds all key-values whose keys start with the substring `term`.
        It skips the first `skip` (default: 0) number of results and returns not more than
        `limit` (default: 0) number of items. This is to avoid using up more memory than can be handled by the
        host machine.
        If `limit` is 0, all items are returned since it would make no sense for someone to search
        for zero items.
        :param model: the base model of the results to return
        :param term: the starting substring to check all keys against
        :param skip: the number of the first matched key-value pairs to skip
        :param limit: the maximum number of records to return at any one given time
        :return: the list of value whose key starts with the `term`
        """
        raise NotImplementedError("search not implemented")

    @abstractmethod
    async def delete(self, k: str) -> None:
        """
        Removes the key-value for the given key from the store
        :param k: the key as a UTF-8 string
        """
        raise NotImplementedError("delete not implemented")

    @abstractmethod
    async def clear(self) -> None:
        """
        Removes all data in the store
        """
        raise NotImplementedError("clear not implemented")
