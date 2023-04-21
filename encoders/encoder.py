from abc import ABC, abstractclassmethod
from typing import Any, Generator

class Encoder(ABC):
    """
    Abstract encoder class for all encoding solutions to derive from.
    """

    @abstractclassmethod
    def get_content_type(cls) -> str:
        pass

    @abstractclassmethod
    def encode(cls, input: Generator[bytes, Any, None]) -> Generator[bytes, Any, None]:
        pass
