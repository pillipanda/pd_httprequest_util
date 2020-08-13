from abc import ABC, abstractmethod


class HttpConnection(ABC):
    @abstractmethod
    def create(self, conn_total_limit: int, conn_limit_per_host: int): ...

    @abstractmethod
    def change_session(self): ...

    @abstractmethod
    def close(self): ...
