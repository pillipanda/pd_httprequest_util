import requests

from pd_httprequest_util.connection.main import HttpConnection


class SyncConnection(HttpConnection):
    @classmethod
    def create(cls, conn_total_limit=100, limit_per_host=0):
        self = cls()
        self.limit = conn_total_limit
        self.limit_per_host = limit_per_host

        self._session = requests.session()
        _adapter = requests.adapters.HTTPAdapter(
            pool_connections=conn_total_limit,
            pool_maxsize=conn_total_limit,
            max_retries=3,  # applies only to failed DNS lookups, socket connections and connection timeouts
        )
        self._session.mount('http://', _adapter)
        self._session.mount('https://', _adapter)
        return self

    @property
    def session(self):
        return self._session

    def change_session(self):
        self.close()
        new_ins = self.create(
            conn_total_limit=self.limit,
            limit_per_host=self.limit_per_host
        )
        self._session = new_ins.session

    def close(self):
        self._session.close()
