from abc import ABC, abstractmethod


class HttpReqer(ABC):
    @abstractmethod
    def create(self, conn_total_limit: int, conn_limit_per_host: int): ...

    @abstractmethod
    def change_conn(self): ...

    @abstractmethod
    def close(self): ...
