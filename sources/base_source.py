from abc import ABC, abstractmethod
from database.models import Product


class BaseSource(ABC):

    @abstractmethod
    def fetch_product(self, url: str) -> Product:
        pass
