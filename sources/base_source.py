from abc import ABC, abstractmethod


class BaseSource(ABC):

    @abstractmethod
    def get_product(self, url):
        """
        Return a Product object.
        """
        pass
